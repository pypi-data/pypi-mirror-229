
from .__lib_abstractions__ import ObjectEncoder, ArrayEncoder
from .Statement import Statement
from functools import cached_property
import requests
import json
import sys
import re
from typing import Union


xsrfTokens: dict[str, str] = {}
baseUrl = "https://admanager.google.com/dfp/v2/exchange/rpc"


class GAMSession(requests.Session):
    def __init__(self, gam_id: str, service_name: str, cookie: Union[dict, str] = {}):
        super().__init__()
        self.gam_id = gam_id
        self.headers = {}
        self.headers["cookie"] = cookie
        self.endpoint = f"{baseUrl}/{service_name}"
        try:
            self.headers["x-framework-xsrf-token"] = self.xsrfToken
        except Exception as err:
            raise Exception(f"Authorization failed couldn't obtain a xrsf-token")
        self.headers["content-type"] = "application/json"
        self.params = {
            "networkCode": f"{gam_id}",
            "authuser": "0"
        }

    @property
    def xsrfToken(self):
        global xsrfTokens
        if self.gam_id not in xsrfTokens:
            response = self.get(f"https://admanager.google.com/{self.gam_id}")
            xsrfTokens[self.gam_id] = re.search(r"'xsrfToken': {0,}'(.*?)'", response.text).group(1)  # group(1) matches the first parenthesized subgroup (.*?)\
        return xsrfTokens[self.gam_id]

    def post(self, *args, **kwds):
        """
        GAMSession manages the correct url endpoint.
        ```python
        (method) def post(
            data: _Data | None = None,
            json: Incomplete | None = None,
            *,
            params: _Params | None = ...,
            headers: _HeadersUpdateMapping | None = ...,
            cookies: RequestsCookieJar | _TextMapping | None = ...,
            files: _Files | None = ...,
            auth: _Auth | None = ...,
            timeout: _Timeout | None = ...,
            allow_redirects: bool = ...,
            proxies: _TextMapping | None = ...,
            hooks: _HooksInput | None = ...,
            stream: bool | None = ...,
            verify: _Verify | None = ...,
            cert: _Cert | None = ...
        ) -> Response
        ```
        """
        return super().post(self.endpoint, *args, **kwds)


class GAMCredentials:
    """
    GAMCredentials merely decodes a cookie.

    The cookie is passed in the `__ini__` argumtent in the form of a `str` or `dict`.

    The `__init__` tries to extract a valid cookie that'll be used in order to authorize the Service's session
    """

    def __init__(self, gam_id, cookie):
        """Extract a valid cookie that'll be used in order to authorize the Service's session"""
        if not (type(gam_id) is int or type(gam_id) is str and gam_id.isdigit()):
            raise TypeError(f"""The gam_id must be of type {int}""")
        self.gam_id = gam_id
        cookieKey = "__Secure-1PSID"
        if type(cookie) is str:
            ixCookie = max(0, cookie.find(cookieKey) + len(cookieKey) + 1)   # returns 0 in case not found (-1)
            ixDelim = max(0, cookie.find(";", ixCookie)) or None  # returns a positive int or None
            cookie = cookie[ixCookie:ixDelim]
            if len(cookie) <= len(cookieKey) + 1:
                raise TypeError(f'The cookie must contain a property "{cookieKey}"')
            if not cookie.startswith(cookieKey):
                cookie = f"{cookieKey}={cookie}"
            self.cookie = cookie
        elif type(cookie) is dict:
            if cookieKey not in cookie:
                raise TypeError(f'The cookie must contain a property "{cookieKey}"')
            elif type(cookie[cookieKey]) is not str:
                raise TypeError(f"""The value in cookie["{cookieKey}"] must be of type {str}""")
            self.cookie = f"{cookieKey}={cookie[cookieKey]}"
        else:
            raise TypeError(f"The cookie must be of type {str} or {dict}")


class GAMService(GAMCredentials):
    """
    Common Google Ad Manager Services obtain resources in similair ways and require the same Session.

    GAMService defines a cached_property session and a method getResourceByStatement.
    ```python
    class GAMService(GAMCredentials):
        session: GAMSession
        getResourceByStatement(self, resource, page, totalResultSetSize, startIndex, results, DataModel, statement): list[resources]
    ```
    """
    @cached_property
    def session(self):
        """
        Common Google Ad Manager Sessions require similair property attributes.
        ```python
        baseUrl: 'https://admanager.google.com/dfp/v2/exchange/rpc'
        class GAMSession(requests.Session):
            xsrfToken: str
            def __init__(self, gam_id: str, service_name: str, cookie: dict | str): None
                self.gam_id: str
                self.headers: dict['cookie': str, 'x-framework-xsrf-token': str, 'content-type': 'application/json']
                self.endpoint: f"{baseUrl}/{service_name}"
                self.params: dict['networkCode': str, 'authuser': str]
            def post(self, *args, **kwds): Response
        ```
        """
        return GAMSession(self.gam_id, self.__class__.__name__, self.cookie)

    def getResourceByStatement(self, resource: str, page: str, totalResultSetSize: str, startIndex: str, results: str, DataModel: ArrayEncoder, statement: Statement):
        """Common Google Ad Manager Services in general follow the pattern coded in this method in order to get resources by statement."""
        method = sys._getframe(1).f_code.co_name

        if not isinstance(statement, Statement):
            raise Exception(f"The argument statement must be instance of {Statement}")

        errors = []
        resources = DataModel(*[])
        while True:
            response = self.session.post(data=json.dumps({
                "method": method,
                "params": {
                    resource: {
                        "1981": statement.toStatement()
                    }
                }
            }))
            resultJson = response.json()
            if "result" not in resultJson:
                errors.append(f"""{response}: {response.text}""")
                errors.append("""Was expecting a property "result" in the response""")
            elif page not in resultJson["result"]:
                errors.append(f"""Was expecting response["result"]["{page}"]: page""")
            elif totalResultSetSize not in resultJson["result"][page]:
                errors.append(f"""Was expecting response["result"][page]["{totalResultSetSize}"]: totalResultSetSize""")
            elif startIndex not in resultJson["result"][page]:
                errors.append(f"""Was expecting response["result"][page]["{startIndex}"]: startIndex""")
            elif results not in resultJson["result"][page]:
                errors.append(f"""Was expecting response["result"][page]["{results}"]: results""")
            elif type(resultJson["result"][page][results]) is not list:
                errors.append(f"""Was expecting Was expecting response["result"][page][results] to be a {list}""")
            if errors:
                raise Exception("\n\b".join([f"{self.__class__.__name__}.getResourceByStatement"] + errors))
            resources.extend(DataModel(*resultJson["result"][page][results]))
            if not statement.next(resultJson["result"][page][totalResultSetSize]):
                break

        return resources
