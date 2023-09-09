
from .__lib__ import *
import json


@ServiceManager().manage
class PricingRuleService(GAMService):
    def getPricingRulesByStatement(self, statement: dict) -> list[PricingRule]:
        """
        Google Ad Manager doesn't officially provide `PricingRuleService` and therefore no API docs exist.
        ```
        validStatementExample = {
            "filters": {
                "OR": [{
                    "AND": [
                        ("Name", "LIKE", "floor_bb_%"),
                        ["Status", "IN", ["Active"]]
                    ]
                }, ("Name", "LIKE", "floor_hpa_0_%")]
            },
            "LIMIT": 100,
            "OFFSET": 0
        }
        anotherValidStatementExample = { "filters": ("Name", "LIKE", "floor_iab_%") }

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
        pricingRules = "358"
        page = "3440"
        totalResultSetSize = "1405"
        startIndex = "1839"
        results = "3400"
        return self.getResourceByStatement(pricingRules, page, totalResultSetSize, startIndex, results, PricingRules, statement)

    def createPricingRule(self, pricingRule: dict) -> PricingRule:
        errors = []
        body = {
            "method": "createPricingRule",
            "params": {
                "2": {
                    "1119": "15705759192818615013"
                },
                "1532": PricingRule(**pricingRule)
            }
        }
        response = self.session.post(data=json.dumps(body)).json()

        if "result" not in response:
            errors.append("""Was expecting a property "result" in the response""")
        elif "1097" not in response["result"]:
            errors.append("""Was expecting a property "1097" in the response["result"]""")
        elif type(response["result"]["1097"]) is not dict:
            errors.append(f"""Was expecting a {dict} in the response["result"]["1097"]""")
        else:
            return PricingRule(**response["result"]["1097"])
        raise Exception("\n\b".join(["PricingRuleService.createPricingRule"] + errors))

    def updatePricingRule(self, pricingRule) -> PricingRule:
        errors = []
        body = {
            "method": "updatePricingRule",
            "params": {
                "2": {
                    "1119": "4729396451099967141"
                },
                "55": PricingRule(**pricingRule)
            }
        }
        response = self.session.post(data=json.dumps(body)).json()

        if "result" not in response:
            errors.append("""Was expecting a property "result" in the response""")
        elif "490" not in response["result"]:
            errors.append("""Was expecting a property "490" in the response["result"]""")
        elif type(response["result"]["490"]) is not dict:
            errors.append(f"""Was expecting a {dict} in the response["result"]["490"]""")
        else:
            return PricingRule(**response["result"]["490"])
        raise Exception("\n\b".join(["PricingRuleService.updatePricingRule"] + errors))

    def findPricingRulesByTargetedAdUnits(self, targetedAdUnits: list[int]) -> list[PricingRule]:
        if not all(isinstance(id, int) for id in targetedAdUnits):
            raise Exception("\n\b".join(["PricingRuleService.findPricingRules"] + ["The argument targetedAdUnitsmust be a list[int]"]))
        pricingRules = self.getPricingRulesByStatement({"filters": ["Status", "IN", ["Active"]]})
        return list(filter(
            lambda pricingRule:
            "inventoryTargeting" in pricingRule["targeting"] and
            "targetedAdUnits" in pricingRule["targeting"]["inventoryTargeting"] and
            isinstance(pricingRule["targeting"]["inventoryTargeting"]["targetedAdUnits"], list) and
            any(
                adUnitId in targetedAdUnits
                for adUnitId in pricingRule["targeting"]["inventoryTargeting"]["targetedAdUnits"]
            ), pricingRules))
