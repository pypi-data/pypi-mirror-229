
from .__lib_AccountPolicySummary__ import AccountPolicySummary
from typing import TypedDict


class Internal(TypedDict):
    accountPolicySummary: AccountPolicySummary
    debug: bool


internal = Internal()
