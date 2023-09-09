
from functools import cached_property
import json
from .__lib__ import *


@ServiceManager().manage
class PolicyService(GAMCredentials):
    @cached_property
    def session(self) -> 'PolicySession':
        return PolicySession(self.gam_id, self.cookie)

    def getEntityPolicyStats(self) -> list[EntityPolicyStat]:
        self.getAccountPolicySummary()
        response = self.session.post(
            f"https://admanager.google.com/display-ads-policy-center/acx/proto/GetEntityPolicyStats",
            data=json.dumps({"3": True}))
        return EntityPolicyStats(*json.loads(response.text[6:])["adsense.fe.policy.GetEntityPolicyStatsResponse"]["1"])

    @cache_expire()
    def getAccountPolicySummary(self):
        response = self.session.post(
            f"https://admanager.google.com/display-ads-policy-center/acx/proto/GetAccountPolicySummary",
            data=json.dumps({"1": "en_US"}))
        internal["accountPolicySummary"] = AccountPolicySummary(**json.loads(response.text[6:])["adsense.fe.policy.GetAccountPolicySummaryResponse"])
        return internal["accountPolicySummary"]
