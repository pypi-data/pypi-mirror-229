from steampye.confirmation import ConfirmationExecutor
from steampye.constants import COMMUNITY_URL
from steampye.models import (UserSellListingBox, UserBuyOrderBox, UserHistoryListingBox, PriceOverview, SaleData,
                             MarketListingBox, Currency, Game, ItemSaleHistory)
from steampye.exceptions import SteamServerError, SteampyException, ParameterError, ApiException
from steampye.session import SteamSession, login_required
from steampye.utils import extract_json, text_between


class BasicMarket:
    def __init__(self, steam_session: SteamSession):
        self.session = steam_session

    def fetch_price(self, market_hash_name: str, game: Game, currency=Currency.USD) -> dict:
        url = COMMUNITY_URL + '/market/priceoverview/'
        params = {'currency': currency, 'appid': game.app_id, 'market_hash_name': market_hash_name}
        response = self.session.get(url, params=params)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    def get_sale_data(self, item_name_id=None, currency=Currency.USD) -> dict:

        url = COMMUNITY_URL + "/market/itemordershistogram"
        params = {"language": "english", "currency": currency, "item_nameid": item_name_id}
        response = self.session.get(url, params=params)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    @login_required
    def get_item_sale_history(self, market_hash_name: str, game: Game):
        url = COMMUNITY_URL + "/market/pricehistory"
        params = {"appid": game.app_id, "market_hash_name": market_hash_name}
        response = self.session.get(url, params=params)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    def get_item_name_id(self, market_hash_name: str, game: Game) -> str:
        url = COMMUNITY_URL + "/market/listings/%s/%s" % (game.app_id, market_hash_name)
        response = self.session.get(url)
        response = self.session.handle_steam_response(response)
        item_name_id = text_between(response.text, "Market_LoadOrderSpread( ", " )").strip()
        return item_name_id

    def get_item_listings(self, market_hash_name: str, game: Game, currency=Currency.USD, count=10,
                          start=0) -> dict:
        url = COMMUNITY_URL + "/market/listings/%s/%s/render" % (game.app_id, market_hash_name)
        params = {'currency': currency, 'query': "", 'language': "english", "start": start, "count": count}
        response = self.session.get(url, params=params)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        return response_json

    @login_required
    def get_my_sell_listing(self, count=30, start=0) -> dict:
        params = {"start": start, "count": count, "norender": 1}
        url = COMMUNITY_URL + "/market/mylistings"
        response = self.session.get(url, params=params)

        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") is False or response_json.get("total_count") is None:
            raise SteamServerError("Invalid response, data: %s" % response_json)

        return response_json

    @login_required
    def get_my_sell_listing_to_confirm(self) -> dict:
        return BasicMarket.get_my_buy_orders(self)

    @login_required
    def get_my_buy_orders(self) -> dict:
        params = {"norender": 1, "count": 1}
        url = COMMUNITY_URL + "/market/mylistings"
        response = self.session.get(url, params=params)

        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") is False or response_json.get("total_count") is None:
            raise SteamServerError("Invalid response, data: %s" % response_json)

        return response_json

    @login_required
    def get_my_market_history(self, count=10, start=0) -> dict:
        params = {"start": start, "count": count, "norender": 1}
        url = COMMUNITY_URL + "/market/myhistory"
        response = self.session.get(url, params=params)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") is False or response_json.get("total_count") is None:
            raise SteamServerError(f"Invalid response, data: {response_json}")

        return response_json

    @login_required
    def create_sell_order(self, asset_id: str, game: Game, money_to_receive: int, _confirm=True) -> dict:
        data = {
            "assetid": asset_id,
            "sessionid": self._get_session_id(),
            "contextid": game.context_id,
            "appid": game.app_id,
            "amount": 1,
            "price": money_to_receive
        }
        headers = {'Referer': "%s/profiles/%s/inventory" % (COMMUNITY_URL, self.session.steam_id)}
        response = self.session.post(COMMUNITY_URL + "/market/sellitem/", data, headers=headers)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)
        if _confirm and response_json.get("needs_mobile_confirmation"):
            return self._confirm_sell_listing(asset_id)
        return response_json

    @login_required
    def create_buy_order(self, market_name: str, price_single_item: int, quantity: int, game: Game,
                         currency: Currency = Currency.USD, billing_info=None) -> dict:
        data = {
            "sessionid": self._get_session_id(),
            "currency": currency,
            "appid": game.app_id,
            "market_hash_name": market_name,
            "price_total": price_single_item * quantity,
            "quantity": quantity
        }
        if billing_info:
            data["first_name"] = billing_info["first_name"]
            data["last_name"] = billing_info["last_name"]
            data["billing_address"] = billing_info["billing_address"]
            data["billing_address_two"] = billing_info["billing_address_two"]
            data["billing_country"] = billing_info["billing_country"]
            data["billing_city"] = billing_info["billing_city"]
            data["billing_state"] = billing_info["billing_state"]
            data["billing_postal_code"] = billing_info["billing_postal_code"]

        headers = {'Referer': "%s/market/listings/%s/%s" % (COMMUNITY_URL, game.app_id, market_name)}
        response = self.session.post(COMMUNITY_URL + "/market/createbuyorder/", data, headers=headers)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") != 1:
            more_text = f"Api message: {response_json['message']}" if "message" in response_json else ""
            raise ApiException(f"There was a problem creating the order. {more_text}")
        return response_json

    @login_required
    def cancel_sell_order(self, sell_listing_id: str):
        """Steam return nothing from this call"""
        data = {"sessionid": self._get_session_id()}
        headers = {'Referer': COMMUNITY_URL + "/market/"}
        url = "%s/market/removelisting/%s" % (COMMUNITY_URL, sell_listing_id)
        response = self.session.post(url, data=data, headers=headers)
        response = self.session.handle_steam_response(response)

    @login_required
    def cancel_buy_order(self, buy_order_id) -> dict:
        data = {"sessionid": self._get_session_id(), "buy_orderid": buy_order_id}
        headers = {"Referer": COMMUNITY_URL + "/market"}
        response = self.session.post(COMMUNITY_URL + "/market/cancelbuyorder/", data, headers=headers)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") != 1:
            raise ApiException("There was a problem canceling the order. success: %s" % response_json.get("success"))
        return response_json

    @login_required
    def get_buy_order_status(self, buy_order_id):
        params = {"sessionid": self._get_session_id(), "buy_orderid": buy_order_id}
        headers = {"Referer": COMMUNITY_URL + "/market"}
        response = self.session.get(COMMUNITY_URL + "/market/getbuyorderstatus/", params=params, headers=headers)
        response = self.session.handle_steam_response(response)
        response_json = extract_json(response)

        if response_json.get("success") != 1:
            raise ApiException("There was a problem getting the buy order status. "
                               "success: %s" % response_json.get("success"))
        return response_json

    def _confirm_sell_listing(self, asset_id: str) -> dict:
        con_executor = ConfirmationExecutor(self.session.steam_guard['identity_secret'],
                                            self.session.steam_guard['steamid'],
                                            self.session)
        try:
            return con_executor.confirm_sell_listing(asset_id)
        except Exception as e:
            raise SteamServerError("[CONFIRM_SELL_LISTING_ERROR]") from e

    def _get_session_id(self) -> str:
        return self.session.cookies.get_dict()['sessionid']


class Market(BasicMarket):
    def __init__(self, steam_session: SteamSession):
        super().__init__(steam_session)

    def fetch_price(self, market_hash_name: str, game: Game, currency: str = Currency.USD) -> PriceOverview:
        data = super().fetch_price(market_hash_name, game, currency)

        if not PriceOverview.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            price_overview = PriceOverview.create(data)

        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return price_overview

    def get_sale_data(self, market_hash_name=None, game: Game = None, currency=Currency.USD,
                      item_name_id=None) -> SaleData:
        if not ((market_hash_name and game) or item_name_id):
            raise ParameterError("One parameter is required")

        if not item_name_id:
            item_name_id = super().get_item_name_id(market_hash_name, game)

        data = super().get_sale_data(item_name_id, currency)

        if not SaleData.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            sale_data = SaleData.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return sale_data

    def get_item_sale_history(self, market_hash_name: str, game: Game):
        data = super().get_item_sale_history(market_hash_name, game)
        if not ItemSaleHistory.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)

        try:
            item_sale_history = ItemSaleHistory.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return item_sale_history

    def get_item_listings(self, market_hash_name: str, game: Game, currency=Currency.USD, count=10,
                          start=0) -> MarketListingBox:
        data = super().get_item_listings(market_hash_name, game, currency, count, start)

        if not MarketListingBox.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            market_listing_box = MarketListingBox.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return market_listing_box

    def get_my_sell_listing(self, count=None, start=0) -> UserSellListingBox:
        data = super().get_my_sell_listing(count, start)

        if not UserSellListingBox.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            listings_box = UserSellListingBox.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return listings_box

    def get_my_sell_listing_to_confirm(self) -> UserSellListingBox:
        data = super().get_my_sell_listing_to_confirm()

        if not UserSellListingBox.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            del data["listings"]
            data["listings"] = data["listings_to_confirm"]
            listings_box = UserSellListingBox.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return listings_box

    def get_my_buy_orders(self) -> UserBuyOrderBox:
        data = super().get_my_buy_orders()

        if not UserBuyOrderBox.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            orders_box = UserBuyOrderBox.create(data["buy_orders"])
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return orders_box

    def get_my_market_history(self, count=30, start=0) -> UserHistoryListingBox:
        data = super().get_my_market_history(count, start)

        if not UserHistoryListingBox.is_well_formed(data):
            raise SteamServerError("Response not well formed", data=data)
        try:
            history_box = UserHistoryListingBox.create(data)
        except Exception as e:
            raise SteampyException(f"Error while creating the model", data=data) from e

        return history_box
