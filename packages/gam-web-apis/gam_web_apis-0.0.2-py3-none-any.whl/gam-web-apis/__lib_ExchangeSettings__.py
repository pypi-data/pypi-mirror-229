
from .__lib_abstractions__ import *


class AdExchangeLink(ObjectEncoder):
    code: str = Class("543", str)


class AdExchangeLinks(ArrayEncoder):
    Encoder = AdExchangeLink


class ExchangeSettings(ObjectEncoder):
    pid: str = Class("863", str)
    adExchangeLinks: list[AdExchangeLink] = Class("2281", AdExchangeLinks)
