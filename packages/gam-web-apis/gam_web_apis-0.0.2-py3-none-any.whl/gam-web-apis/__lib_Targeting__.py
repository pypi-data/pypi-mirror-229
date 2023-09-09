
from .__lib_abstractions__ import *


class LocationCoordinates(ObjectEncoder):
    longitude: float = Class("1911", float)
    latitude: float = Class("3965", float)


class UnknownCoordinates(ObjectEncoder):
    unknownCoordinates1: LocationCoordinates = Class("1172", LocationCoordinates)
    unknownCoordinates2: LocationCoordinates = Class("3218", LocationCoordinates)


class LocationData(ObjectEncoder):
    longitudeId: int = Class("29", int)
    centerCoordinates: LocationCoordinates = Class("833", LocationCoordinates)
    canonicalParentIds: list[int] = Class("931", list)
    latitudeId: int = Class("1024", int)
    displayName: str = Class("1163", str)
    parentCountryId: str = Class("1220", str)
    type: str = Class("1573", str)
    unknownCoordinates: UnknownCoordinates = Class("2317", UnknownCoordinates)
    countryCode: str = Class("2477", str)
    parentCountryCode: str = Class("3210", str)

    def __init__(self, **input):
        super().__init__(**input)
        self['96'] = True
        self["2784"] = True


class Location(ObjectEncoder):
    datamodel: str = Label("2", "Location", 581777835)
    id: int = Lambda("259", int, str)
    canonicalParentId: int = Class("2183", int)
    type: str = Class("2739", str)
    displayName: str = Class("3040", str)
    data: LocationData = Class("4028", LocationData)


class Locations(ArrayEncoder):
    Encoder = Location


class TechnologyVersion(ObjectEncoder):
    minor: str = Class("2542", str)
    major: str = Class("3246", str)


class Technology(ObjectEncoder):
    datamodel: str = Switch("2", ("Browser", 2058270449), ("DeviceCategory", 97714507), ("OperatingSystem", 63845753))
    version: TechnologyVersion = Class("528", TechnologyVersion)
    name: str = Class("1410", str)
    id: int = Lambda("2585", int, str)


class Technologies(ArrayEncoder):
    Encoder = Technology


class Criteria(ObjectEncoder):
    datamodel: str = Switch("2", ("Browser", 2058270449), ("DeviceCategory", 97714507), ("OperatingSystem", 63845753), required=True)
    technology: Technology = Class("136", Technology)


class CriteriaList(ArrayEncoder):
    Encoder = Criteria
