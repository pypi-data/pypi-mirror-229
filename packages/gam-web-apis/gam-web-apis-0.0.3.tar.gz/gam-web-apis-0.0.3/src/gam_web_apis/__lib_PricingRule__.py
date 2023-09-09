
from .__lib_abstractions__ import *
from .__lib_Targeting__ import *


class AdUnitTargeting(ObjectEncoder):
    id: int = Lambda("892", int, str)
    included: bool = Class("1825", bool, required=True)


class AdUnitTargetingList(ArrayEncoder):
    Encoder = AdUnitTargeting


class InventoryTargeting(ObjectEncoder):
    targetedAdUnits: list[AdUnitTargeting] = Class("1738", AdUnitTargetingList)
    excludedAdUnits: list[AdUnitTargeting] = Class("3772", AdUnitTargetingList)


class GeoTargeting(ObjectEncoder):
    targetedLocations: list[Location] = Class("3075", Locations)
    excludedLocations: list[Location] = Class("2077", Locations)


class BrowserTargeting(ObjectEncoder):
    browsers: list[Technology] = Class("707", Technologies)
    isTargeted: bool = Class("3786", bool)


class DeviceCategoryTargeting(ObjectEncoder):
    targetedDeviceCategories: list[Technology] = Class("2488", Technologies)
    excludedDeviceCategories: list[Technology] = Class("3166", Technologies)


class OperatingSystemTargeting(ObjectEncoder):
    operatingSystems: Technologies = Class("2499", Technologies)
    isTargeted: bool = Class("290", bool)


class ChildOperatingSystemTargeting(ObjectEncoder):
    operatingSystems: Technologies = Class("245", Technologies)


class TechnologyTargeting(ObjectEncoder):
    browserTargeting: BrowserTargeting = Class("1225", BrowserTargeting)
    operatingSystemTargeting: OperatingSystemTargeting = Class("1543", OperatingSystemTargeting)
    deviceCategoryTargeting: DeviceCategoryTargeting = Class("2381", DeviceCategoryTargeting)
    childOperatingSystemTargeting: ChildOperatingSystemTargeting = Class("3125", ChildOperatingSystemTargeting)
    # bandwidthGroupTargeting = Class("NOT SUPPORTED", None)
    # browserLanguageTargeting = Class("NOT SUPPORTED", None)
    # deviceCapabilityTargeting = Class("NOT SUPPORTED", None)
    # deviceManufacturerTargeting = Class("NOT SUPPORTED", None)
    # mobileCarrierTargeting = Class("NOT SUPPORTED", None)
    # mobileDeviceTargeting = Class("NOT SUPPORTED", None)
    # mobileDeviceSubmodelTargeting = Class("NOT SUPPORTED", None)
    # operatingSystemVersionTargeting = Class("NOT SUPPORTED", None)


class CustomCriteria(ObjectEncoder):
    keyId: int = Lambda("463", int, str)
    operator: str = Switch("1713", ("IS", 2346), ("IS_NOT", 2125479394))
    valueIds: list[int] = Lambda("4080", decode=lambda ids: [int(id) for id in ids], encode=lambda ids: [str(id) for id in ids])


class CustomCriteriaList(ArrayEncoder):
    Encoder: CustomCriteria = CustomCriteria.extends("CustomCriteriaLeaf", "3559", inherits={
        "2197": 2052813759
    }).extends("CustomCriteriaNode", "3253", inherits={
        "2": 506444345,
        "1392": "0"
    })


class CustomCriteriaSetLvl2(ObjectEncoder):
    logicalOperator: str = Switch("660", ("AND", 64951), required=True)
    children: list[CustomCriteria] = Class("3360", CustomCriteriaList, required=True)


class CustomCriteriaSetLvl2List(ArrayEncoder):
    Encoder = CustomCriteriaSetLvl2.extends("CustomCriteriaNode", "2253", inherits={
        "2": 736710939,
        "1392": "0"
    })


class CustomCriteriaSetLvl1(ObjectEncoder):
    logicalOperator: str = Switch("660", ("OR", 2531), required=True)
    children: list[CustomCriteriaSetLvl2] = Class("3360", CustomCriteriaSetLvl2List, required=True)


class Targeting(ObjectEncoder):
    inventoryTargeting: InventoryTargeting = Class("845", InventoryTargeting)
    customTargeting: CustomCriteriaSetLvl1 = Class("2253", CustomCriteriaSetLvl1).extends(
        "CustomCriteriaNode", "881", inherits={
            "2": 736710939,
            "1392": "0"
        })
    geoTargeting: GeoTargeting = Class("1085", GeoTargeting)
    technologyTargeting: TechnologyTargeting = Class("3417", TechnologyTargeting)

    def __init__(self, **input):
        super().__init__(**input)
        self['3792']: False


class Size(ObjectEncoder):
    height: int = Class("749", int, required=True)
    width: int = Class("3602", int, required=True)

    def __init__(self, **input):
        super().__init__(**input)
        self['350'] = 76143206
        self['3452'] = False


class SizeList(ArrayEncoder):
    Encoder = Size


class SizeOptions(ObjectEncoder):
    included: bool = Class("1033", bool, default=True)
    sizes: list[Size] = Class("1575", SizeList, default=[])


class PricingOptions(ObjectEncoder):
    sizeOptions: SizeOptions = Class("3785", SizeOptions, default={})

    def __init__(self, **input):
        super().__init__(**input)
        self['403'] = {}
        self['1337'] = {}
        self['2077'] = {}
        self['2929'] = {}


def encodeEuro(euro):
    euro = round(float(euro), 2)
    if euro < 0.01:
        raise Exception("""The value of the property "branded" of a pricing must be greater or equal to 0.01""")
    return {
        "385": "EUR",
        "2182": str(int(euro * 1000000))
    }


def decodeEuro(input):
    return round(int(input["2182"]) / 1000000, 2)


class Pricing(ObjectEncoder):
    type: str = Switch("903", ("FLOOR_PRICE", 66989036), ("TARGET_CPMS", 1827576431), required=True)
    branded: float = Lambda("1021", decodeEuro, encodeEuro, required=True)
    options: PricingOptions = Class("3684", PricingOptions, default={})


class PricingList(ArrayEncoder):
    Encoder = Pricing


class PricingRule(ObjectEncoder):
    id: int = Lambda("151", int, str)
    status: str = Switch("1025", ("ACTIVE", 1925346054), ("INACTIVE", 807292011), default="ACTIVE")
    targeting: Targeting = Class("2103", Targeting, required=True)
    pricing: list[Pricing] = Class("3171", PricingList, required=True)
    name: str = Class("3844", str, required=True)

    def __init__(self, **input):
        super().__init__(**input)
        self['2377'] = False


class PricingRules(ArrayEncoder):
    Encoder = PricingRule
