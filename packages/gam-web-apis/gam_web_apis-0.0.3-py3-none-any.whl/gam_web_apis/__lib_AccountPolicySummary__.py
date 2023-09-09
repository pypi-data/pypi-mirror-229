
from .__lib_abstractions__ import *


class PolicyViolation(ObjectEncoder):
    id: int = Class("1", int)
    issue: str = Class("2", str)


class PolicyViolations(ArrayEncoder):
    Encoder = PolicyViolation


class AccountPolicySummary(ObjectEncoder):
    unknownFeature: list[int] = Class("10", list)
    policyViolations: list[PolicyViolation] = Class("5", PolicyViolations)
