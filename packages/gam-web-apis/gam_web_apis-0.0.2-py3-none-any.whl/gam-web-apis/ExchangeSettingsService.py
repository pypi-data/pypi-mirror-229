
from .__lib_ServiceManager__ import ServiceManager
from .__lib_session__ import GAMService
from .__lib_ExchangeSettings__ import ExchangeSettings
from .__lib_tools__ import cache_expire
import json


@ServiceManager().manage
class ExchangeSettingsService(GAMService):
    @cache_expire()
    def getCurrentExchangeSettings(self):
        response = self.session.post(data=json.dumps({
            "method": "getCurrentExchangeSettings",
            "params": {}
        }))
        return ExchangeSettings(**response.json()['result']['750'])
