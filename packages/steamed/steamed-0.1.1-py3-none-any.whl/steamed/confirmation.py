import json
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from .guard import generate_device_id, generate_confirmation_key
from .exceptions import ConfirmationExpected, SteamServerError
from .login import InvalidCredentials


class ConfType:
    TRADEOFFER = 2
    SELL_LISTING = 3


class Confirmation:
    def __init__(self, id_, nonce, creator_id):
        self.id = id_
        self.nonce = nonce
        self.creator_id = creator_id

        self.type = None
        self.type_name = None
        self.creation_time = None
        self.type = None
        self.icon = None
        self.multi = None
        self.headline = None
        self.summary = None
        self.warn = None

    @staticmethod
    def from_dict(dconf) -> "Confirmation":
        nonce = dconf["nonce"]
        id_ = dconf["id"]
        creator_id = dconf["creator_id"]
        conf = Confirmation(id_, nonce, creator_id)
        conf.type = dconf.get("type")
        conf.type_name = dconf.get("type_name")
        conf.creation_time = dconf.get("creation_time")
        conf.icon = dconf.get("icon")
        conf.multi = dconf.get("multi")
        conf.headline = dconf.get("headline")
        conf.summary = dconf.get("summary")
        conf.warn = dconf.get("warn")
        return conf


class Tag:
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, my_steam_id: str, session: requests.Session) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session

    def confirm_trade_offer(self, trade_offer_id: str) -> dict:
        confirmations = self.get_confirmations()
        confirmation = self._select_trade_offer_confirmation(confirmations, trade_offer_id)
        return self.send_confirmation(confirmation)

    def confirm_sell_listing(self, asset_id: str) -> dict:
        confirmations = self.get_confirmations()

        try:
            confirmation = self._select_sell_listing_confirmation(confirmations, asset_id)
        except Exception as e:
            raise SteamServerError("Steam Error while selecting the confirmation for "
                                   "assetid: %s" % asset_id, data=confirmations) from e

        return self.send_confirmation(confirmation)

    def send_confirmation(self, confirmation: Confirmation) -> dict:
        params = self._create_confirmation_params(Tag.ALLOW)
        params['op'] = Tag.ALLOW
        params['cid'] = confirmation.id
        params['ck'] = confirmation.nonce
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        return self._session.get(self.CONF_URL + '/ajaxop', params=params, headers=headers).json()

    def send_multiple_confirmations(self, confs: List[Confirmation]):
        params = self._create_confirmation_params(Tag.ALLOW)
        params['op'] = Tag.ALLOW
        params["cid[]"] = []
        params["ck[]"] = []
        for conf in confs:
            params["cid[]"].append(conf.id)
            params["ck[]"].append(conf.nonce)
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        return self._session.post(self.CONF_URL + '/multiajaxop', data=params, headers=headers).json()

    def get_confirmations(self) -> Dict[str, Confirmation]:
        confirmations = {}
        conf_resp = self._fetch_confirmations_page()
        jresp = conf_resp.json()

        for dconf in jresp.get("conf", []):
            conf = Confirmation.from_dict(dconf)
            confirmations[conf.creator_id] = conf

        return confirmations

    def _fetch_confirmations_page(self) -> requests.Response:
        params = self._create_confirmation_params(Tag.CONF)
        headers = {'X-Requested-With': 'com.valvesoftware.android.steam.community'}
        response = self._session.get(self.CONF_URL + '/getlist', params=params, headers=headers)
        if 'Steam Guard Mobile Authenticator is providing incorrect Steam Guard codes.' in response.text:
            raise InvalidCredentials('Invalid Steam Guard file')
        return response

    def _fetch_confirmation_details_page(self, confirmation: Confirmation) -> str:
        tag = 'details' + confirmation.id
        params = self._create_confirmation_params(tag)
        response = self._session.get(self.CONF_URL + '/details/' + confirmation.id, params=params)
        return response.json()['html']

    def _create_confirmation_params(self, tag_string: str) -> dict:
        timestamp = int(time.time())
        confirmation_key = generate_confirmation_key(self._identity_secret, tag_string, timestamp)
        android_id = generate_device_id(self._my_steam_id)
        return {'p': android_id,
                'a': self._my_steam_id,
                'k': confirmation_key,
                't': timestamp,
                'm': 'android',
                'tag': tag_string}

    def _select_trade_offer_confirmation(self, confirmations: Dict[str, Confirmation],
                                         trade_offer_id: str) -> Confirmation:
        if trade_offer_id in confirmations:
            return confirmations[trade_offer_id]

        raise ConfirmationExpected

    def _select_sell_listing_confirmation(self, confirmations: Dict[str, Confirmation],
                                          asset_id: str) -> Confirmation:
        for confirmation in confirmations.values():
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_sell_listing_id(confirmation_details_page)
            if confirmation_id == asset_id:
                return confirmation
        raise ConfirmationExpected

    @staticmethod
    def _get_confirmation_sell_listing_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        scr_raw = str(soup.select("script")[2])
        scr_raw = scr_raw[scr_raw.index("'confiteminfo', ") + 16:]
        scr_raw = scr_raw[:scr_raw.index(", UserYou")].replace("\n", "")
        return json.loads(scr_raw)["id"]

    @staticmethod
    def _get_confirmation_trade_offer_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        full_offer_id = soup.select('.tradeoffer')[0]['id']
        return full_offer_id.split('_')[1]
