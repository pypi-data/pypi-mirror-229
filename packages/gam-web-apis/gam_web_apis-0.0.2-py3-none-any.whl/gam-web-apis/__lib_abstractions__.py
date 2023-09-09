
from typing import Union
import glob
import json


if not hasattr(glob, "debug"):
    glob.debug = False


def color(msg, st, c, bg):
    return f"\x1b[{st};{c};{bg}m{msg}\x1b[0m"


class DecoderBase:
    def extends(self: Union['PropertyDecoder', 'DecoderExtends'], extensionName: str, accessor: str, inherits: dict = {}):
        return DecoderExtends(extensionName, accessor, self, inherits)


class PropertyDecoder(DecoderBase):
    def __init__(self, encodedName: str, required=False, default=None):
        self.__encoded_name__ = encodedName
        self.__required__ = required
        self.__default__ = default

    def __set_name__(self, owner, decodedName: str):
        self.__decoded_name__ = decodedName

    def __get__(self, instance: Union['ObjectEncoder', dict], __owner: type):
        if self.__encoded_name__ in instance:
            return instance[self.__encoded_name__]

    def __set__(self, instance: 'ObjectEncoder', value):
        instance[self.__encoded_name__] = value

    def __contains__(self, name: str):
        return name in (self.__decoded_name__, self.__encoded_name__)

    def __initialize__(self, encoder: 'ObjectEncoder', input: dict):
        value = input.get(self.__decoded_name__, None)
        if value is None:
            if self.__encoded_name__ in input:
                value = self.__get__(input, input.__class__)
            elif value is None:
                value = getattr(encoder, self.__decoded_name__, None)
        if value is not None:
            if glob.debug:
                print(f"{self.__class_name__(encoder.__class__)} is set to {value}")
            setattr(encoder, self.__decoded_name__, value)
        elif self.__required__:
            raise KeyError(f"{self.__class_name__(encoder.__class__)} is required")
        elif self.__default__ is not None:
            if glob.debug:
                print(f"{self.__class_name__(encoder.__class__)} by default is to {self.__default__}")
            setattr(encoder, self.__decoded_name__, self.__default__)

    def __class_name__(self, owner: type, extends=''):
        return f"<class {owner.__name__}>[{extends}<{self.__class__.__name__} {self.__decoded_name__} '{self.__encoded_name__}'>]"


class DecoderExtends(DecoderBase):
    def __init__(self, extensionName: str, accessor: str, decoder: 'PropertyDecoder', inherits: dict = {}):
        self.__extension_name__ = extensionName
        self.__accessor__ = accessor
        self.__decoder__ = decoder
        self.__inherits__ = inherits

    def __set_name__(self, owner, decodedName: str):
        self.__decoder__.__set_name__(owner, decodedName)

    def __get__(self, instance: Union['ObjectEncoder', dict], __owner: type):
        return self.__decoder__.__get__(instance[self.__accessor__], __owner)

    def __set__(self, instance: 'ObjectEncoder', value):
        self.__decoder__.__set__(instance[self.__accessor__], value)

    def __contains__(self, name: str):
        return name == self.__decoder__.__decoded_name__

    def __initialize__(self, encoder: 'ObjectEncoder', input: dict):
        encoder[self.__accessor__] = input.get(self.__accessor__, {})
        filteredInput = {**encoder[self.__accessor__], **{key: value for key, value in input.items() if key in self}}
        for key, value in self.__inherits__.items():
            encoder[self.__accessor__].setdefault(key, value)
        self.__decoder__.__initialize__(encoder, filteredInput)

    @ property
    def __decoded_name__(self):
        return self.__decoder__.__decoded_name__

    def __class_name__(self, owner: type, extends=''):
        return self.__decoder__.__class_name__(owner, extends=f"{extends}<{self.__class__.__name__} {self.__extension_name__} {json.dumps(self.__accessor__)}>, ")


class PropertyDecoders(list[Union[PropertyDecoder, DecoderExtends]]):
    def __contains__(self, name):
        return any(name in decoder for decoder in self)


class EncoderBase(dict):
    @ classmethod
    def extends(Encoder: Union['ObjectEncoder', 'EncoderExtendsObject'], extensionName: str, accessor: str, inherits: dict = {}):
        class Extends(EncoderExtendsObject):
            __Encoder__ = Encoder
            __extension_name__ = extensionName
            __accessor__ = accessor
            __inherits__ = inherits
        return Extends


class ObjectEncoder(EncoderBase):
    def __init__(self, **input):
        super().__init__((key, value) for key, value in input.items() if key not in self.__property_decoders__)
        for decoder in self.__property_decoders__:
            decoder.__initialize__(self, input)

    @ property
    def decode(self):
        return {
            decoder.__decoded_name__: value.decode if isinstance(value, (EncoderBase, ArrayEncoder)) else value
            for decoder in self.__property_decoders__
            if (value := getattr(self, decoder.__decoded_name__)) is not None
        }

    def __init_subclass__(cls):
        cls.__property_decoders__ = PropertyDecoders(prop for prop in cls.__dict__.values() if isinstance(prop, DecoderBase))
        super().__init_subclass__()

    @ classmethod
    def __class_name__(self):
        return f"<class {self.__name__}"


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class EncoderExtendsObject(EncoderBase):
    __Encoder__: Union['ObjectEncoder', 'EncoderExtendsObject']
    __extension_name__: str
    __accessor__: str
    __inherits__: dict

    def __init__(self, **input):
        super().__init__((key, value) for key, value in input.items() if key not in self)
        for key, value in self.__inherits__.items():
            self.setdefault(key, value)
        filteredInput = dict(((key, value) for key, value in input.items() if key in self), **input.get(self.__accessor__, {}))
        self[self.__accessor__] = self.__Encoder__(**filteredInput)

    @ property
    def decode(self):
        return {
            decoder.__decoded_name__: value.decode if isinstance(value, (EncoderBase, ArrayEncoder)) else value
            for decoder in self.__property_decoders__
            if (value := getattr(self, decoder.__decoded_name__)) is not None
        }

    def __contains__(self, name: str):
        return any(name == decoder.__decoded_name__ for decoder in self.__property_decoders__)

    def __init_subclass__(cls):
        cls.__property_decoders__ = PropertyDecoders()
        for decoder in cls.__Encoder__.__property_decoders__:
            extended = decoder.extends(cls.__extension_name__, cls.__accessor__)
            setattr(cls, decoder.__decoded_name__, extended)
            extended.__set_name__(cls, decoder.__decoded_name__)
            cls.__property_decoders__.append(extended)

    @ classmethod
    def __class_name__(self):
        return f"<class Extends {self.__extension_name__} '{self.__accessor__}'>[{self.__Encoder__.__class_name__()}]"


class ArrayEncoder(list[Union[ObjectEncoder, EncoderExtendsObject]]):
    def __init__(self, *iterable: dict):
        super().__init__([self.Encoder(**input) for input in iterable])

    @ property
    def decode(self):
        return [encoder.decode for encoder in self]

    @ classmethod
    def __class_name__(self):
        return f"<class {self.__name__}"


class Lambda(PropertyDecoder):
    def __init__(self, encodedName, decode, encode, **options):
        super().__init__(encodedName, **options)
        self.decode = decode
        self.encode = encode

    def __get__(self, instance, __owner):
        return self.decode(super().__get__(instance, __owner))

    def __set__(self, instance, value):
        if value is not None:
            super().__set__(instance, self.encode(value))


class Switch(PropertyDecoder):
    def __init__(self, encodedName, *couples, **options):
        super().__init__(encodedName, **options)
        self.__couples__ = [(decoded, encoded) for decoded, encoded in map(tuple, couples)]

    def __get__(self, instance, __owner):
        encoded = super().__get__(instance, __owner)
        return next((decoded for decoded, __encoded in self.__couples__ if encoded in (decoded, __encoded)), None)

    def __set__(self, instance, value):
        if value is not None:
            encoded = next((__encoded for decoded, __encoded in self.__couples__ if decoded == value), None)
            if encoded is not None:
                super().__set__(instance, encoded)


class Class(PropertyDecoder):
    def __init__(self, encodedName, model, **options):
        super().__init__(encodedName, **options)
        self.model = model

    def __get__(self, instance, __owner):
        __value = super().__get__(instance, __owner)
        if __value is not None:
            if isinstance(__value, self.model):
                return __value
            elif issubclass(self.model, dict):
                return self.model(**__value)
            elif issubclass(self.model, list):
                return self.model(*__value)
            else:
                return self.model(__value)

    def __set__(self, instance, value):
        if value is not None:
            super().__set__(
                instance,
                value if isinstance(value, self.model) else
                self.model(**value) if issubclass(self.model, dict) else
                self.model(*value) if issubclass(self.model, list) else
                value)


class Label(PropertyDecoder):
    def __init__(self, encodedName, label, value, **options):
        super().__init__(encodedName, **options)
        self.label = label
        self.value = value

    def __get__(self, instance, __owner):
        return self.label

    def __set__(self, instance, value):
        instance[self.__encoded_name__] = self.value
