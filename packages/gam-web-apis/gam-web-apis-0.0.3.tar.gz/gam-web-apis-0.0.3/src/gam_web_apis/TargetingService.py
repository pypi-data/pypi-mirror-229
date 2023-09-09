
from .__lib__ import *
import json


@ServiceManager().manage
class TargetingService(GAMService):
    def getGeoTargetCountries(self) -> list[Location]:
        body = {
            "method": "getGeoTargetCountries",
            "params": {
                "1555": 0
                # TODO figure out precisely what this value is meant to represent,
                # 0: returns all countries (244),
                # 1: returns a few countries (around 20),
                # 2: returns almost all countries (around 200)
                # 3: returns no countries
            }
        }
        response = self.session.post(data=json.dumps(body))
        resJson = response.json()
        if "result" not in resJson or "2679" not in resJson["result"]:
            print(f"getGeoTargetCountries", response.status_code, response.text)
            return []
        return Locations(*response.json()["result"]["2679"])

    def getChildrenGeoTargets(self, location_id) -> list[Location]:
        body = {
            "method": "getChildrenGeoTargets",
            "params": {
                "1467": location_id
            }
        }
        response = self.session.post(data=json.dumps(body))
        resJson = response.json()
        if "result" not in resJson or "231" not in resJson["result"]:
            print(f"getChildrenGeoTargets", response.status_code, response.text)
            return []
        return Locations(*resJson["result"]["231"])

    def getCriterionByStatement(self, statement) -> list[Criteria]:
        """
        This method is built in order to fetch various types of [TechnologyTargeting]('https://developers.google.com/ad-manager/api/reference/v202302/TargetingPresetService.TechnologyTargeting'). Google Ad Manager doesn't officially provide `TargetingService` but instead provides the [TargetingPresetService]('https://developers.google.com/ad-manager/api/reference/v202302/TargetingPresetService'). However, `PricingRuleService` requires serialization and deserialization of [TechnologyTargeting]('https://developers.google.com/ad-manager/api/reference/v202302/TargetingPresetService.TechnologyTargeting') models and therefore support for the `TargetingService` is required.
        ```
        safari_browser_statement = {
            "AND": [
                ("Type", "IN", ['Browser']),
                "{Safari}"
            ]
        }
        phone_deviceCategories_statement = {
            "AND": [
                ("Type", "IN", ['DeviceCategory']),
                "{phone}"
            ]
        }
        xBox_operatingSystem_statement = {
            "AND": [
                ("Type", "IN", ['OperatingSystem']),
                "{Xbox}"
            ]
        }
        variousTypes_statement = ("Type", "IN", ['Browser', 'DeviceCategory', 'OperatingSystem'])

        class Statement(TypedDict):
            filters: <Query> | <NestedQuery>
            LIMIT:   <int>
            OFFSET:  <int>
            ORDER:   "Name ASC" | "Name DESC"

        class NestedQuery(TypedDict):
            OR:  <list[Query]>
            AND: <list[Query]>

        class Query(Iterable):
            0: property  - ["Name", "Status", "Id"]
            1: operation - "IN"   | "IS"   | "LIKE"           | "<" | "<=" | ">" | ">=" | "=" | "!="
            2: value     - <list> | "NULL" | <wildcard%match> | <value> or <bind variable>

        ```"""
        technologies = "2626"
        page = "1082"
        totalResultSetSize = "2347"
        startIndex = "2781"
        results = "2458"
        return self.getResourceByStatement(technologies, page, totalResultSetSize, startIndex, results, CriteriaList, statement)
