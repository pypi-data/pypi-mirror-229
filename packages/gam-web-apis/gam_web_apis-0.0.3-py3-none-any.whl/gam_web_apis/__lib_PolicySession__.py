
import requests
import json
import re
from .ExchangeSettingsService import ExchangeSettingsService

xsrfTokens: dict[str, str] = {}
publisherIds: dict[str, str] = {}


def loadJson(varName, text):
    varMatched = re.search(varName + r'[^{]*({[^;]*});', text).group(1)
    # Regexp explained: [^{]*({[^;]*});
    #    1. [^{]*    Match anything that's not a '{' char
    #    2. ({       Followed by the exact char '{'
    #    3. [^;]*    Followed by anything that's not a ';' char
    #    4. });      Followed by the exact sequence of '};' chars
    #    5. ({ * })  Select everything in from '{' untill '}' as group(1)
    varEncoded = re.sub(r',(\s|\n)*}', '}', varMatched.replace("'\\x7b", "{").replace("\\x7d'", "}").replace("'", '"'))
    varDecoded = bytes(varEncoded, "utf-8").decode("unicode_escape")
    return json.loads(varDecoded)


class PolicySession(requests.Session):
    def __init__(self, gam_id, cookie={}):
        super().__init__()
        self.gam_id = gam_id
        self.headers = {}
        self.headers["cookie"] = cookie
        self.params = {
            "host": "drx",
            "nc": f"{self.gam_id}",
            "pid": ExchangeSettingsService(gam_id, cookie).getCurrentExchangeSettings().pid,
        }
        self.headers["x-framework-xsrf-token"] = self.xsrfToken
        self.headers["content-type"] = "application/json"

    @property
    def xsrfToken(self):
        global xsrfTokens
        if self.gam_id not in xsrfTokens:
            response = self.post(url=f"https://admanager.google.com/display-ads-policy-center/policy-center-v4/loader", params={
                "hl": "en-US"
            })
            try:
                # pid = loadJson('__policy_center_params', response.text)['pid']
                xsrfTokens[self.gam_id] = loadJson('__policy_center_metadata', response.text)['token']
            except Exception as err:
                raise Exception(f"Authorization failed couldn't obtain a xrsf-token")
        return xsrfTokens[self.gam_id]
