
from .__lib_abstractions__ import *
from .__lib_internal__ import internal
from typing import Optional


class Page(ObjectEncoder):
    site = Class("1", str, required=True)
    url = Class("2", str, required=True)


class PolicyViolation(ObjectEncoder):
    name: int = Lambda("1", required=True,
                       decode=lambda issue_id: next(policyViolation for policyViolation in internal["accountPolicySummary"].policyViolations if policyViolation.id == issue_id).issue,
                       encode=lambda issue: next(policyViolation for policyViolation in internal["accountPolicySummary"].policyViolations if policyViolation.issue == issue).id)
    must_fix: bool = Class("2", bool, required=True)


class Issues(ArrayEncoder):
    Encoder = PolicyViolation.extends("Issue", "1")


class RegisteredIssues(ObjectEncoder):
    issues: list[PolicyViolation] = Class("9", Issues, required=True)
    date: str = Lambda("10",
                       decode=lambda dt: ({"year": int(dt[:4]), "month": int(dt[4:6]), "day": int(dt[6:])}),
                       encode=lambda dt: f'{dt["year"]}{str(dt["month"]).zfill(2)}{str(dt["day"]).zfill(2)}')


class IssuesRegisty(ArrayEncoder):
    Encoder = RegisteredIssues


class EntityPolicyStat(ObjectEncoder):
    adRequests: int = Lambda("4", int, str)
    issuesRegister: list[RegisteredIssues] = Class("5", IssuesRegisty, required=True)
    entity: str = Switch("11", ("page", 4), ("site", 2), required=True)
    site: Optional[str] = Class("12", str)
    page: Optional[Page] = Class("14", Page)


class EntityPolicyStats(ArrayEncoder):
    Encoder = EntityPolicyStat
