
from .__lib__ import *
import json


class Protection:
    @property
    def decode(self):
        """I have not yet made any attempt to decode Google-Ad-Manager-compatible-object-notation to software-developer-understandable-object-notation"""
        return self


@ServiceManager().manage
class ProtectionService(GAMService):
    def getProtectionsByStatement(self, statement: dict):
        protections = "1455"
        page = "4027"
        totalResultSetSize = "1317"
        startIndex = "1751"
        results = "3488"
        return self.getResourceByStatement(protections, page, totalResultSetSize, startIndex, results, Protection, statement)
