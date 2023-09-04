import json
from typing import List, Union

from steampye import guard
from steampye.confirmation import ConfirmationExecutor
from steampye.constants import COMMUNITY_URL, STORE_URL
from steampye.utils import extract_json, get_token_from_trade_offer_url, \
    get_partner_from_trade_offer_url, account_id_to_steam_id, steam_id_to_account_id, texts_between
from .market import Market, BasicMarket
from .models import TradeOffersBox, TradeOffer, TradeReceipt, Inventory, Game, BasicAsset
from .exceptions import SteamServerError, SteampyException, InvalidTradeOfferID, ParameterError, TradeHoldException
from .session import SteamSession, login_required


class BasicClient:
    def __init__(self, api_key: str = None) -> None:
        super().__init__()
        self.session = SteamSession()
        self.market = self._create_market(self.session)

        if api_key:
            self.api_key = api_key

    def _create_market(self, session: SteamSession) -> BasicMarket:
        return BasicMarket(session)

    @property
    def api_key(self) -> str:
        return self.session.api_key

    @api_key.setter
    def api_key(self, api_key: str):
        self.session.api_key = api_key

    def login(self, username: str, password: str, steam_guard: Union[str, dict]) -> None:
        self.session.login(username, password, steam_guard)

    @login_required
    def relogin(self):
        self.session.relogin()

    def logout(self) -> None:
        raise NotImplementedError

    def is_session_alive(self) -> bool:
        if not self.session.steam_id:
            return False

        url = f"https://steamcommunity.com/profiles/{self.session.steam_id}/notifications"
        head_response = self.session.head(url)
        return head_response.status_code == 200

    def get_player_inventory(self, steam_id: str, game: Game, count=0) -> dict:
        """ Return the inventory of the player by steam_id. 'count' can go up to 5000."""
        url = f"{COMMUNITY_URL}/inventory/{steam_id}/{game.app_id}/{game.context_id}/?l=english"
        if count:
            url = url + f"&count={count}"

        response = self.session.get(url)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    @login_required
    def get_my_inventory(self, game: Game, count=0) -> dict:
        """
        Return your inventory. 'count' can go up to 5000.
        This method is intended to be shorter than 'get_player_inventory(...)' but login is
        required.
        """
        return self.get_player_inventory(self.session.steam_id, game, count)

    @login_required
    def send_trade_offer(self,
                         items_to_give: List[BasicAsset],
                         items_to_receive: List[BasicAsset],
                         message: str = None,
                         partner_steam_id: str = None,
                         trade_offer_url: str = None,
                         check_trade_hold=True,
                         _confirm=True) -> dict:
        """
        Send a Steam trade offer.
        If the partner is your Steam friend, you can pass his steam_id.
        If the partner is not your friend on Steam, you need to pass his trade_offer_url.
        'message' can be omitted.
        If 'check_trade_hold' is set to True the offer will not be sent if the items will be put on hold after the trade
        """
        token = None
        trade_offer_create_params = {}
        if trade_offer_url:
            token = get_token_from_trade_offer_url(trade_offer_url)
            partner_account_id = get_partner_from_trade_offer_url(trade_offer_url)
            partner_steam_id = account_id_to_steam_id(partner_account_id)
            trade_offer_create_params["trade_offer_access_token"] = token
            referer = trade_offer_url

        elif partner_steam_id:
            partner_steam_id = account_id_to_steam_id(partner_steam_id)
            partner_account_id = steam_id_to_account_id(partner_steam_id)
            referer = COMMUNITY_URL + '/tradeoffer/new/?partner=' + partner_account_id

        else:
            raise ParameterError("A 'trade_offer_url' or a 'partner_steam_id' is needed to use this method")

        if check_trade_hold:
            json_response = self.get_trade_hold_durations(partner_steam_id, token)
            trade_hold_duration = json_response["both_escrow"]["escrow_end_duration_seconds"]
            if trade_hold_duration != 0:
                raise TradeHoldException("Offer not sent because otherwise items will be on hold")

        offer = self._create_offer_dict(items_to_give, items_to_receive)
        params = {
            'sessionid': self._get_session_id(),
            'serverid': 1,
            'partner': partner_steam_id,
            'tradeoffermessage': message,
            'json_tradeoffer': json.dumps(offer),
            'captcha': '',
            'trade_offer_create_params': json.dumps(trade_offer_create_params)
        }
        headers = {'Referer': referer, 'Origin': COMMUNITY_URL}
        response = self.session.post(COMMUNITY_URL + '/tradeoffer/new/send', data=params, headers=headers)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if _confirm and response_json.get('needs_mobile_confirmation'):
            if "tradeofferid" not in response_json:
                raise SteamServerError("Steam responded without a 'tradeofferid'")

            confirmation_response_dict = self._confirm_trade_offer(response_json['tradeofferid'])
            response_json.update(confirmation_response_dict)
        return response_json

    @login_required
    def accept_trade_offer(self, trade_offer_id: str, partner_steam_id: str = None, check_trade_hold=True) -> dict:
        """
        Accept a trade offer.
        You can make this method faster (one less request to steam endpoint) if you provide 'partner_steam_id' and set
        'check_trade_hold' to False.
        Do that only if you already know that no trade hold will be issued when accepting this offer.
        This is useful when you fetch a trade offer from 'get_trade_offers(...)' or 'get_trade_offer(...)' so you
        already have all the required information.
        """
        if check_trade_hold or not partner_steam_id:
            offer = self.get_trade_offer(trade_offer_id)["response"]["offer"]

            if check_trade_hold and offer["escrow_end_date"] != 0:
                raise TradeHoldException("Offer not accepted because items will be put on hold")

            if not partner_steam_id:
                partner_steam_id = offer["accountid_other"]

        partner_steam_id = account_id_to_steam_id(partner_steam_id)
        accept_url = COMMUNITY_URL + '/tradeoffer/' + trade_offer_id + '/accept'
        params = {'sessionid': self._get_session_id(),
                  'tradeofferid': trade_offer_id,
                  'serverid': '1',
                  'partner': partner_steam_id,
                  'captcha': ''}
        headers = {'Referer': COMMUNITY_URL + '/tradeoffer/' + trade_offer_id}
        # todo check what goes wrong if the offer is no longer active
        response = self.session.post(accept_url, data=params, headers=headers)

        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get('needs_mobile_confirmation', False):
            return self._confirm_trade_offer(trade_offer_id)  # todo check the return values
        return response_json

    def decline_trade_offer(self, trade_offer_id: str) -> dict:
        data = {'sessionid': self._get_session_id()}
        url = f"{COMMUNITY_URL}/tradeoffer/{trade_offer_id}/decline"
        response = self.session.post(url=url, data=data)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    # if it's mine
    def cancel_trade_offer(self, trade_offer_id: str) -> dict:
        data = {'sessionid': self._get_session_id()}
        url = f"https://steamcommunity.com/tradeoffer/{trade_offer_id}/cancel"
        response = self.session.post(url=url, data=data)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    def get_trade_offers(self,
                         sent_offers=True,
                         received_offers=True,
                         descriptions=True,
                         active_only=True,
                         historical_only=False,
                         time_historical_cutoff="",
                         language="english") -> dict:

        params = {'get_sent_offers': 1 if sent_offers else 0,
                  "get_received_offers": 1 if received_offers else 0,
                  "get_descriptions": 1 if descriptions else 0,
                  "language": language,
                  'active_only': 1 if active_only else 0,
                  'historical_only': 0 if historical_only else 0,
                  'time_historical_cutoff': time_historical_cutoff}
        response_json = self.session.api_call('GET', 'IEconService', 'GetTradeOffers', 'v1', params)
        return response_json

    def get_trade_offer(self, trade_offer_id: str, get_descriptions: bool = False) -> dict:
        """get_descriptions only works if the offer is active"""
        params = {'tradeofferid': trade_offer_id, 'language': 'english', "get_descriptions": get_descriptions}
        response_json = self.session.api_call('GET', 'IEconService', 'GetTradeOffer', 'v1', params)
        return response_json

    def get_trade_offers_summary(self) -> dict:
        response_json = self.session.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1')
        return response_json

    def get_trade_history(self,
                          max_trades=100,
                          start_after_time=None,
                          start_after_tradeid=None,
                          get_descriptions=True,
                          navigating_back=False,
                          include_failed=True) -> dict:
        params = {
            'max_trades': max_trades,
            'start_after_time': start_after_time,
            'start_after_tradeid': start_after_tradeid,
            'get_descriptions': 1 if get_descriptions else 0,
            'navigating_back': 1 if navigating_back else 0,
            'include_failed': 1 if include_failed else 0,
            'include_total': 1
        }
        response_json = self.session.api_call('GET', 'IEconService', 'GetTradeHistory', 'v1', params)
        return response_json

    @login_required
    def get_trade_receipt(self, trade_id: str) -> list:
        url = COMMUNITY_URL + "/trade/" + trade_id + "/receipt"
        response = self.session.get(url)
        response = self.session.handle_steam_response(response)
        html = response.text
        items = []
        for item in texts_between(html, "oItem = ", ";\r\n\toItem"):
            items.append(json.loads(item))

        return items

    def get_trade_hold_durations(self, player_steam_id, trade_offer_access_token: str = None) -> dict:
        """
        'trade_offer_access_token' can be found in the trade offer url of that player.
        If the player is your friend on Steam no token is required.
        """
        params = {"steamid_target": player_steam_id, "trade_offer_access_token": trade_offer_access_token}
        response_json = self.session.api_call("GET", "IEconService", "GetTradeHoldDurations", "v1", params)
        return response_json

    @login_required
    def get_confirmation_executor(self) -> ConfirmationExecutor:
        conf_executor = ConfirmationExecutor(self.session.steam_guard['identity_secret'],
                                             self.session.steam_id,
                                             self.session)
        return conf_executor

    @login_required
    def generate_two_factor_code(self) -> str:
        return guard.generate_one_time_code(self.session._login_executor.shared_secret)

    def _get_session_id(self) -> str:
        return self.session.cookies.get_dict()['sessionid']

    @staticmethod
    def _create_offer_dict(items_to_give: List[BasicAsset], items_to_receive: List[BasicAsset]) -> dict:
        return {
            'newversion': True,
            'version': 4,
            'me': {
                'assets': [asset.to_dict() for asset in items_to_give],
                'currency': [],
                'ready': False
            },
            'them': {
                'assets': [asset.to_dict() for asset in items_to_receive],
                'currency': [],
                'ready': False
            }
        }

    def _confirm_trade_offer(self, trade_offer_id: str) -> dict:
        conf_executor = ConfirmationExecutor(self.session.steam_guard['identity_secret'],
                                             self.session.steam_id,
                                             self.session)
        try:
            return conf_executor.confirm_trade_offer(trade_offer_id)
        except Exception as e:
            raise SteamServerError("[CONFIRM_TRADE_OFFER_ERROR]") from e


class Client(BasicClient):

    def __init__(self, api_key: str):
        self.market = None
        super().__init__(api_key)

    def _create_market(self, session: SteamSession) -> Market:
        return Market(self.session)

    def get_trade_offer(self, trade_offer_id: str, get_descriptions: bool = False) -> TradeOffer:
        data = super().get_trade_offer(trade_offer_id, get_descriptions=get_descriptions)

        if not data:
            raise InvalidTradeOfferID("No tradeoffer found with id %s" % trade_offer_id)

        if not TradeOffer.is_well_formed(data, single_trade_offer=True):
            raise SteamServerError("Response not well formed, data: %s" % data)
        try:
            trade_offer = TradeOffer.create(data, single_trade_offer=True)
        except Exception as e:
            raise SteampyException("TODO") from e

        return trade_offer

    def get_trade_offers(self,
                         sent_offers=True,
                         received_offers=True,
                         descriptions=True,
                         active_only=True,
                         historical_only=False,
                         time_historical_cutoff="",
                         language="english") -> TradeOffersBox:

        data = super().get_trade_offers(sent_offers,
                                        received_offers,
                                        descriptions,
                                        active_only,
                                        historical_only,
                                        time_historical_cutoff,
                                        language)

        if not TradeOffersBox.is_well_formed(data):
            raise SteamServerError("Response not well formed, data: %s" % data)
        try:
            trade_offer_box = TradeOffersBox.create(data)
        except Exception as e:
            raise SteampyException("TODO") from e

        return trade_offer_box

    def get_player_inventory(self, steam_id: str, game: Game, count=0) -> Inventory:
        data = super().get_player_inventory(steam_id, game, count)

        if not Inventory.is_well_formed(data):
            raise SteamServerError("Response not well formed, data: %s" % data)
        try:
            inventory = Inventory.create(data)
        except Exception as e:
            raise SteampyException("TODO") from e

        return inventory

    def get_my_inventory(self, game: Game, count=0) -> Inventory:
        return self.get_player_inventory(self.session.steam_id, game, count)

    def get_trade_receipt(self, trade_id: str) -> TradeReceipt:
        data = super().get_trade_history(max_trades=1, start_after_tradeid=trade_id, get_descriptions=True)

        if not TradeReceipt.is_well_formed(data):
            raise SteamServerError("Response not well formed, data: %s" % data)
        try:
            receipt = TradeReceipt.create(data)
        except Exception as e:
            raise SteampyException("TODO") from e

        return receipt
