from typing import Union, Optional

import requests

from .constants import API_URL
from .utils import extract_json
from .guard import load_steam_guard
from .login import LoginExecutor
from .exceptions import SteamServerError, LoginRequired, InvalidCredentials, LoginException, \
    TooManyRequests


def login_required(func):
    def func_wrapper(self, *args, **kwargs):

        on_before_login_required(self, *args, **kwargs)

        _login_executor = None
        if hasattr(self, "session") and isinstance(self.session, SteamSession):
            _login_executor = self.session._login_executor

        if not _login_executor:
            raise LoginRequired('Use login method first')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def _default_before_login_required(self, *args, **kwargs):
    pass

on_before_login_required = _default_before_login_required


class SteamSession(requests.Session):
    def __init__(self):
        super().__init__()
        self._login_executor = None  # type: LoginExecutor

        self.steam_guard = {}
        self.steam_id = None  # type: str
        self.api_key = None  # type: str

    def login(self, username: str, password: str, steam_guard: Union[str, dict]) -> None:
        if type(steam_guard) == dict:
            self.steam_guard = steam_guard
        else:
            self.steam_guard = load_steam_guard(steam_guard)

        self._login_executor = LoginExecutor(username, password, self.steam_guard['shared_secret'],
                                             self)
        self._login()

    def relogin(self):
        if self._login_executor:
            self.cookies.clear_session_cookies()
            self._login()
        else:
            raise LoginRequired("Use login method first")

    def _login(self) -> None:
        try:
            login_response_dict = self._login_executor.login()
            self.steam_id = login_response_dict["steamid"]
        except InvalidCredentials as e:
            raise e
        except Exception as e:
            raise LoginException("Something bad occured") from e

    def api_call(self, request_method: str, interface: str, api_method: str, version: str,
                 params: dict = None) -> dict:

        url = "/".join([API_URL, interface, api_method, version])
        params = params or {}
        if self.api_key:
            params["key"] = self.api_key

        if request_method == 'GET':
            response = self.get(url, params=params)
        else:
            response = self.post(url, data=params)

        if "Please verify your <pre>key=</pre> parameter" in response.text:
            raise InvalidCredentials("Invalid Steam API key")

        self.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    def handle_steam_response(self, response: requests.Response) -> requests.Response:
        if "set-cookie" in response.headers:
            action = response.headers.get("set-cookie")
            if "steamLogin=deleted" in action or "steamLoginSecure=deleted" in action:

                self.relogin()
                creq = response.request.copy()
                del creq.headers["Cookie"]
                creq.prepare_cookies(self.cookies)
                response = self.send(creq)

        if response.status_code == 429:
            raise TooManyRequests("Steam responded with a 429 http code. Too many requests")

        elif response.status_code != 200:
            raise SteamServerError("Steam responded with a %s http code, text: %s" % (
                response.status_code, response.text))

        return response

    def post(self, url, data=None, json=None, **kwargs) -> requests.Response:
        """ Same of requests.post(...) """
        try:
            return super().post(url, data=data, json=json, **kwargs)
        except requests.exceptions.RequestException as e:
            raise SteamServerError() from e

    def get(self, url, **kwargs) -> requests.Response:
        """ Same of requests.get(...) """
        try:
            return super().get(url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise SteamServerError() from e

    def head(self, url, **kwargs) -> requests.Response:
        """ Same of requests.head(...) """
        try:
            return super().head(url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise SteamServerError() from e

    # todo this should be make the session pickle-able
    def __getstate__(self):
        state = super().__getstate__()
        for x, v in self.__dict__.items():
            if x not in state:
                state[x] = v
        return state
