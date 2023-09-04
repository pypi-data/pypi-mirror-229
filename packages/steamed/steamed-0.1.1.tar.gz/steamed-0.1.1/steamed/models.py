from datetime import datetime
from typing import List, Any

import steampye.utils as utils


class Game:
    def __init__(self, app_id, context_id):
        super().__init__()
        self.app_id = app_id
        self.context_id = context_id


class GameOptions:
    DOTA2 = Game('570', '2')
    CSGO = Game('730', '2')
    TF2 = Game('440', '2')
    PUBG = Game('578080', '2')

    @staticmethod
    def new(app_id, context_id):
        return Game(app_id, context_id)


class BasicAsset:
    def __init__(self, asset_id: str, game: Game, amount: int = 1) -> None:
        self.asset_id = asset_id
        self.game = game
        self.amount = amount

    def to_dict(self):
        return {
            'appid': int(self.game.app_id),
            'contextid': self.game.context_id,
            'amount': self.amount,
            'assetid': self.asset_id
        }


class Currency:
    USD = 1
    GBP = 2
    EUR = 3
    CHF = 4
    RUB = 5
    PLN = 6


# Not Basic Objects

class BaseModel:

    @staticmethod
    def create(*args, **kwargs) -> "BaseModel":
        raise NotImplementedError

    @staticmethod
    def is_well_formed(*args, **kwargs) -> bool:
        raise NotImplementedError


class Asset(BaseModel, dict):
    def __init__(self):
        super().__init__()
        self.asset_id = None
        self.app_id = None
        self.class_id = None
        self.instance_id = None
        self.context_id = None
        self.amount = None
        self.description = None

    @staticmethod
    def create(json_dict: dict, description=None) -> "Asset":
        asset = Asset()
        if "assetid" in json_dict:
            asset.asset_id = json_dict["assetid"]
        else:
            asset.asset_id = json_dict["id"]
        asset.app_id = str(json_dict["appid"])
        asset.class_id = str(json_dict["classid"])
        asset.instance_id = str(json_dict["instanceid"])
        asset.context_id = json_dict["contextid"]
        asset.amount = json_dict["amount"]
        asset.description = description

        for field, value in json_dict.items():
            asset[field] = value  # todo add only if not present
        asset["description"] = asset.description

        return asset

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["appid", "classid", "instanceid", "contextid", "amount"]
        for field in fields:
            if field not in json_dict:
                return False

        if "assetid" not in json_dict and "id" not in json_dict:
            return False

        return True


class TradeOfferConfirmationMethod:
    INVALID = 0
    EMAIL = 1
    MOBILE_APP = 2


class TradeOfferState:
    INVALID = 1
    ACTIVE = 2
    ACCEPTED = 3
    COUNTERED = 4
    EXPIRED = 5
    CANCELED = 6
    DECLINED = 7
    INVALID_ITEMS = 8
    CREATED_NEEDS_CONFIRMATION = 9
    CANCELED_BY_SECOND_FACTOR = 10
    IN_ESCROW = 11


class TradeOffer(BaseModel):
    def __init__(self):
        self.trade_offer_id = None  # type: str
        self.account_id_other = None  # type: str
        self.message = None  # type: str
        self.expiration_time = None  # type: datetime
        self.state = None  # type: int
        self.items_to_give = None  # type: List[Asset]
        self.items_to_receive = None  # type: List[Asset]
        self.is_our_offer = None  # type: bool
        self.time_created = None  # type: datetime
        self.time_updated = None  # type: datetime
        self.from_real_time_trade = None  # type: bool
        self.escrow_end_date = None  # type: str
        self.confirmation_method = None  # type: int
        self.trade_id = None  # type: str

    @staticmethod
    def create(json_dict: dict, single_trade_offer=False) -> "TradeOffer":
        """json_dict is the dict from 'get_trade_offer(id)'"""
        descriptions = json_dict.get("descriptions")
        if single_trade_offer:
            json_dict = json_dict["offer"]

        trade_offer = TradeOffer()
        trade_offer.trade_offer_id = json_dict["tradeofferid"]
        trade_offer.account_id_other = json_dict["accountid_other"]
        trade_offer.message = json_dict["message"]
        trade_offer.expiration_time = datetime.utcfromtimestamp(json_dict["expiration_time"])
        trade_offer.state = json_dict["trade_offer_state"]
        trade_offer.is_our_offer = bool(json_dict["is_our_offer"])
        trade_offer.time_created = datetime.utcfromtimestamp(json_dict["time_created"])
        trade_offer.time_updated = datetime.utcfromtimestamp(json_dict["time_updated"])
        trade_offer.from_real_time_trade = bool(json_dict["from_real_time_trade"])
        trade_offer.escrow_end_date = json_dict["escrow_end_date"]
        trade_offer.confirmation_method = json_dict["confirmation_method"]

        if trade_offer.state == TradeOfferState.ACCEPTED:
            trade_offer.trade_id = json_dict["tradeid"]

        descriptions_map = {}
        if descriptions:
            all_assets = json_dict.get("items_to_give", []) + json_dict.get("items_to_receive", [])
            descriptions_map = utils.map_asset_to_descriptions(all_assets, descriptions)

        trade_offer.items_to_give = []
        for item in json_dict.get("items_to_give", []):
            description = None
            if descriptions_map:
                description = descriptions_map[item["assetid"]]
            asset = Asset.create(item, description=description)
            trade_offer.items_to_give.append(asset)

        trade_offer.items_to_receive = []
        for item in json_dict.get("items_to_receive", []):
            description = None
            if descriptions_map:
                description = descriptions_map[item["assetid"]]
            asset = Asset.create(item, description=description)
            trade_offer.items_to_receive.append(asset)

        return trade_offer

    @staticmethod
    def is_well_formed(json_dict: dict, single_trade_offer=False) -> bool:
        if single_trade_offer:
            if "offer" not in json_dict:
                return False
            json_dict = json_dict["offer"]

        fields = ["tradeofferid", "accountid_other", "message", "expiration_time",
                  "trade_offer_state",
                  "is_our_offer", "time_created", "time_updated", "from_real_time_trade",
                  "escrow_end_date",
                  "confirmation_method"]
        for field in fields:
            if field not in json_dict:
                return False

        if json_dict[
            "trade_offer_state"] == TradeOfferState.ACCEPTED and "tradeid" not in json_dict:
            return False

        if (not json_dict.get("items_to_give")) and (not json_dict.get("items_to_receive")):
            return False

        for item in json_dict.get("items_to_give", []):
            if not Asset.is_well_formed(item):
                return False

        for item in json_dict.get("items_to_receive", []):
            if not Asset.is_well_formed(item):
                return False

        return True


class TradeOffersBox(list, BaseModel):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def create(json_dict: dict) -> "TradeOffersBox":
        trade_offer_box = TradeOffersBox()
        offers_list = []
        if "trade_offers_sent" in json_dict:
            offers_list += json_dict["trade_offers_sent"]

        if "trade_offers_received" in json_dict:
            offers_list += json_dict["trade_offers_received"]

        for offer in offers_list:
            trade_offer = TradeOffer.create(offer)
            trade_offer_box.append(trade_offer)

        return trade_offer_box

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        if "trade_offers_sent" in json_dict:
            for offer in json_dict["trade_offers_sent"]:
                if not TradeOffer.is_well_formed(offer):
                    return False

        if "trade_offers_received" in json_dict:
            for offer in json_dict["trade_offers_received"]:
                if not TradeOffer.is_well_formed(offer):
                    return False

        return True


class TradeReceipt(BaseModel, list):

    def __init__(self):
        super().__init__()
        self.trade_id = None  # type: str
        self.steam_id_other = None  # type: str
        self.time_init = None  # type: datetime
        self.status = None  # type: int
        self.total_trades = None  # type: int

    @staticmethod
    def create(json_dict: dict) -> "TradeReceipt":
        trade_receipt = TradeReceipt()

        asset_data = json_dict["trades"][0]
        trade_receipt.trade_id = asset_data["tradeid"]
        trade_receipt.steam_id_other = asset_data["steamid_other"]
        trade_receipt.time_init = datetime.utcfromtimestamp(asset_data["time_init"])
        trade_receipt.status = asset_data["status"]
        trade_receipt.total_trades = json_dict["total_trades"]

        for raw_asset in asset_data.get("assets_received", []):
            raw_asset["old_assetid"] = raw_asset["assetid"]
            raw_asset["assetid"] = raw_asset["new_assetid"]
            trade_receipt.append(Asset.create(raw_asset))

        if "descriptions" in json_dict:
            desc_map = _get_descriptions_map(json_dict["descriptions"])
            _add_descriptions_to_asset(trade_receipt, desc_map)

        return trade_receipt

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        if not json_dict:
            return False

        if "trades" not in json_dict or len(json_dict["trades"]) != 1:
            return False

        if "total_trades" not in json_dict:
            return False

        trade_data = json_dict["trades"][0]
        fields = ["tradeid", "steamid_other", "time_init", "status"]

        for field in fields:
            if field not in trade_data:
                return False

        for asset in trade_data.get("assets_received", []):
            if not Asset.is_well_formed(
                    asset) or "new_assetid" not in asset or "new_contextid" not in asset:
                return False

        return True


class UserSellListing(BaseModel):
    def __init__(self):
        self.listing_id = None  # type: str
        self.time_created = None  # type: datetime
        self.steamid_lister = None  # type: str
        self.price = None  # type: int
        self.original_price = None  # type: int
        self.fee = None  # type: int
        self.currencyid = None  # type: str
        self.converted_price = None  # type: int
        self.converted_fee = None  # type: int
        self.converted_currencyid = None  # type: str
        self.status = None  # type: int
        self.active = None  # type: int
        self.steam_fee = None  # type: int
        self.converted_steam_fee = None  # type: int
        self.publisher_fee = None  # type: int
        self.converted_publisher_fee = None  # type: int
        self.publisher_fee_percent = None  # type: str
        self.publisher_fee_app = None  # type: str
        self.cancel_reason = None  # type: int
        self.item_expired = None  # type: int
        self.original_amount_listed = None  # type: int
        self.original_price_per_unit = None  # type: int
        self.fee_per_unit = None  # type: int
        self.steam_fee_per_unit = None  # type: int
        self.publisher_fee_per_unit = None  # type: int
        self.converted_price_per_unit = None  # type: int
        self.converted_fee_per_unit = None  # type: int
        self.converted_steam_fee_per_unit = None  # type: int
        self.converted_publisher_fee_per_unit = None  # type: int
        self.time_finish_hold = None  # type: int
        self.time_created_str = None  # type: str

        self.asset = None  # type: Asset

    @staticmethod
    def create(json_dict: dict, asset: dict) -> "UserSellListing":
        listing = UserSellListing()
        listing.listing_id = json_dict["listingid"]
        listing.time_created = datetime.utcfromtimestamp(json_dict["time_created"])
        listing.steamid_lister = json_dict["steamid_lister"]
        listing.price = json_dict["price"]
        listing.original_price = json_dict["original_price"]
        listing.fee = json_dict["fee"]
        listing.currencyid = json_dict["currencyid"]
        listing.converted_price = json_dict["converted_price"]
        listing.converted_fee = json_dict["converted_fee"]
        listing.converted_currencyid = json_dict["converted_currencyid"]
        listing.status = json_dict["status"]
        listing.active = json_dict["active"]
        listing.steam_fee = json_dict["steam_fee"]
        listing.converted_steam_fee = json_dict["converted_steam_fee"]
        listing.publisher_fee = json_dict["publisher_fee"]
        listing.converted_steam_fee = json_dict["converted_steam_fee"]
        listing.publisher_fee = json_dict["publisher_fee"]
        listing.converted_publisher_fee = json_dict["converted_publisher_fee"]
        listing.publisher_fee_percent = json_dict["publisher_fee_percent"]
        listing.publisher_fee_app = json_dict["publisher_fee_app"]
        listing.cancel_reason = json_dict["cancel_reason"]
        listing.item_expired = json_dict["item_expired"]
        listing.original_amount_listed = json_dict["original_amount_listed"]
        listing.original_price_per_unit = json_dict["original_price_per_unit"]
        listing.fee_per_unit = json_dict["fee_per_unit"]
        listing.steam_fee_per_unit = json_dict["steam_fee_per_unit"]
        listing.publisher_fee_per_unit = json_dict["publisher_fee_per_unit"]
        listing.converted_price_per_unit = json_dict["converted_price_per_unit"]
        listing.converted_fee_per_unit = json_dict["converted_fee_per_unit"]
        listing.converted_steam_fee_per_unit = json_dict["converted_steam_fee_per_unit"]
        listing.converted_publisher_fee_per_unit = json_dict["converted_publisher_fee_per_unit"]
        listing.time_finish_hold = json_dict["time_finish_hold"]
        listing.time_created_str = json_dict["time_created_str"]

        listing.asset = Asset.create(asset)

        return listing

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True  # todo


class UserBuyOrder(BaseModel):

    def __init__(self):
        self.appid = None  # type: str
        self.buy_orderid = None  # type: str
        self.quantity = None  # type: int
        self.quantity_remaining = None  # type: int
        self.price = None  # type: int
        self.item_name = None  # type: str
        # todo check if other fields can be added

    @staticmethod
    def create(json_dict: dict) -> "UserBuyOrder":
        order = UserBuyOrder()
        order.appid = json_dict["appid"]
        order.buy_orderid = json_dict["buy_orderid"]
        order.quantity = int(json_dict["quantity"])
        order.quantity_remaining = int(json_dict["quantity_remaining"])
        order.price = int(json_dict["price"])
        order.item_name = json_dict["hash_name"]

        return order

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True


class UserSellListingBox(BaseModel, list):

    def __init__(self):
        super().__init__()
        self.total_count = None  # type: int
        self.pagesize = None  # type: int
        self.start = None  # type: int
        self.num_active_listings = None  # type: int

    @staticmethod
    def create(listings_dict: dict) -> "UserSellListingBox":
        box = UserSellListingBox()

        assets = listings_dict["assets"] or {}
        assets_map = utils.get_assets_map(assets)

        for raw_listing in listings_dict["listings"]:
            l_asset = raw_listing["asset"]
            key = (str(l_asset["appid"]), str(l_asset["contextid"]), str(l_asset["id"]))
            asset = assets_map[key]
            listing = UserSellListing.create(raw_listing, asset)
            box.append(listing)

        box.total_count = listings_dict["total_count"]
        box.pagesize = listings_dict["pagesize"]
        box.start = listings_dict["start"]
        box.num_active_listings = listings_dict["num_active_listings"]

        return box

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["total_count", "pagesize", "start", "num_active_listings", "listings"]
        for field in fields:
            if field not in json_dict:
                return False
        return True


# todo fields
class UserBuyOrderBox(BaseModel, dict):

    @staticmethod
    def create(orders_list: list) -> "UserBuyOrderBox":
        box = UserBuyOrderBox()
        for raw_data in orders_list:
            ubo = UserBuyOrder.create(raw_data)
            box[ubo.buy_orderid] = ubo
        return box

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True


class HistoryListingAction:
    CREATED = 1
    CANCELED = 2
    SOLD = 3
    BOUGHT = 4
    EXPIRED = 5


class UserHistoryListing(BaseModel):
    class Event:
        def __init__(self, event: dict):
            self.event_type = event["event_type"]
            self.time_event = datetime.utcfromtimestamp(event["time_event"])
            self.time_event_fraction = event["time_event_fraction"]
            self.steamid_actor = event["steamid_actor"]
            self.date_event = event["date_event"]

    class Purchase:
        def __init__(self, purchase: dict):
            self.purchase_id = purchase["purchaseid"]
            self.time_sold = datetime.utcfromtimestamp(purchase["time_sold"])
            self.steamid_purchaser = purchase["steamid_purchaser"]
            self.needs_rollback = purchase["needs_rollback"]
            self.failed = purchase["failed"]
            self.paid_amount = purchase["paid_amount"]
            self.paid_fee = purchase["paid_fee"]
            self.currencyid = purchase["currencyid"]
            self.steam_fee = purchase["steam_fee"]
            self.publisher_fee = purchase["publisher_fee"]
            self.publisher_fee_percent = purchase["publisher_fee_percent"]
            self.publisher_fee_app = purchase["publisher_fee_app"]
            self.received_amount = purchase["received_amount"]
            self.received_currencyid = purchase["received_currencyid"]
            self.funds_returned = purchase["funds_returned"]
            self.avatar_actor = purchase["avatar_actor"]
            self.persona_actor = purchase["persona_actor"]

            self.asset = Asset.create(purchase["asset"])

    class Listing:
        def __init__(self, listing: dict):
            self.price = listing["price"]
            self.fee = listing["fee"]
            self.publisher_fee_app = listing["publisher_fee_app"]
            self.publisher_fee_percent = listing["publisher_fee_percent"]
            self.original_price = listing["original_price"]

    def __init__(self):
        self.listing_id = None  # type: str
        self.listing = None  # type: UserHistoryListing.Listing
        self.event = None  # type: UserHistoryListing.Event
        self.asset = None  # type: Asset
        self.purchase = None  # type: UserHistoryListing.Purchase
        self.index = None  # type: int

    @staticmethod
    def create(listing: dict, event: dict, asset: dict, purchase: dict,
               index: int) -> "UserHistoryListing":
        uhl = UserHistoryListing()
        uhl.listing_id = listing["listingid"]
        uhl.listing = UserHistoryListing.Listing(listing)
        uhl.event = UserHistoryListing.Event(event)
        if purchase:
            uhl.purchase = UserHistoryListing.Purchase(purchase)
        uhl.asset = Asset.create(asset)
        uhl.index = index

        return uhl

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True


class UserHistoryListingBox(BaseModel, list):

    def __init__(self):
        super().__init__()
        self.page_size = None  # type: int
        self.start = None  # type: int
        self.total_count = None  # type: int

    @staticmethod
    def create(json_dict: dict) -> "UserHistoryListingBox":
        box = UserHistoryListingBox()

        box.page_size = json_dict["pagesize"]
        box.start = json_dict["start"]
        box.total_count = json_dict["total_count"]

        listings_map = {id: listing for id, listing in json_dict["listings"].items()}
        purchases = json_dict.get("purchases") or {}
        purchases_map = {(p["listingid"], p["purchaseid"]): p for p in purchases.values()}
        assets_map = utils.get_assets_map(json_dict["assets"])

        counter = 0
        for event in json_dict["events"]:
            listing_id = event["listingid"]
            listing = listings_map[listing_id]
            l_asset = listing["asset"]
            key = (str(l_asset["appid"]), str(l_asset["contextid"]), str(l_asset["id"]))
            asset = assets_map[key]
            purchase = None
            if "purchaseid" in event:
                purchase = purchases_map.get((listing_id, event["purchaseid"]))

            index = box.total_count - counter - box.start
            uhl = UserHistoryListing.create(listing, event, asset, purchase, index)
            box.append(uhl)

            counter += 1

        return box

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["total_count", "pagesize", "start", "assets", "events", "purchases", "listings"]
        for field in fields:
            if field not in json_dict:
                return False

        # for appid in json_dict["assets"]:
        #     for contextid in json_dict["assets"][appid]:
        #         for asset in json_dict["assets"][appid][contextid]:
        #             if not not Asset.is_well_formed(asset):
        #                 return False
        #
        # e_fields = ["listingid", "event_type", "time_event", "time_event_fraction", "steamid_actor", "date_event"]
        # for field in e_fields:
        #     if field not in json_dict["events"]:
        #         return False

        # Let's assume the other hundreds fields are all right
        return True


class PriceOverview(BaseModel):

    def __init__(self):
        self.lowest_price = None  # type: str
        self.volume = None  # type: int
        self.median_price = None  # type: str

    @staticmethod
    def create(json_dict: dict) -> "PriceOverview":
        price_overview = PriceOverview()

        if "volume" in json_dict:
            price_overview.volume = int(json_dict["volume"])

        if "median_price" in json_dict:
            price_overview.median_price = utils.normalize_price(json_dict["median_price"])

        if "lowest_price" in json_dict:
            price_overview.lowest_price = utils.normalize_price(json_dict["lowest_price"])

        return price_overview

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        if "lowest_price" not in json_dict and "median_price" not in json_dict:
            return False

        return True


class MarketOrder(BaseModel):
    def __init__(self):
        self.price = None  # type: str
        self.cumulative_quantity = None  # type: int

    @staticmethod
    def create(order_data: list) -> "MarketOrder":
        market_order = MarketOrder()
        market_order.price = str(order_data[0] * 100)
        market_order.cumulative_quantity = int(order_data[1])
        return market_order

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True


class SaleData(BaseModel):
    def __init__(self):
        self.sell_orders = None  # type: List[MarketOrder]
        self.buy_orders = None  # type: List[MarketOrder]

    @staticmethod
    def create(json_dict: dict) -> "SaleData":

        sale_data = SaleData()
        sale_data.sell_orders = []
        for order in json_dict["sell_order_graph"]:
            market_order = MarketOrder.create(order)
            sale_data.sell_orders.append(market_order)

        sale_data.buy_orders = []
        for order in json_dict["buy_order_graph"]:
            market_order = MarketOrder.create(order)
            sale_data.buy_orders.append(market_order)

        return sale_data

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["sell_order_graph", "sell_order_table", "sell_order_summary"]

        for field in fields:
            if field not in json_dict:
                return False

        return True


class MarketHistorySale(BaseModel):
    def __init__(self):
        self.price = None  # type: int
        self.sold_count = None  # type: int
        self.sold_date = None  # type: datetime

    @staticmethod
    def create(history_data: list) -> "MarketHistorySale":
        mhs = MarketHistorySale()
        mhs.price = round(history_data[1] * 100)
        mhs.sold_count = int(history_data[2])
        mhs.sold_date = datetime.strptime(history_data[0][:-4], "%b %d %Y %H")
        return mhs

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        return True


class ItemSaleHistory(BaseModel):
    def __init__(self):
        self.price_prefix = None  # type: str
        self.price_suffix = None  # type: str
        self.prices = None  # type: List[MarketHistorySale]

    @staticmethod
    def create(json_dict: dict) -> "ItemSaleHistory":

        ish = ItemSaleHistory()
        ish.price_prefix = json_dict["price_prefix"]
        ish.price_suffix = json_dict["price_suffix"]
        ish.prices = []

        for data in json_dict["prices"]:
            mhs = MarketHistorySale.create(data)
            ish.prices.append(mhs)
        return ish

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["price_prefix", "price_suffix", "prices"]

        for field in fields:
            if field not in json_dict:
                return False

        return True


class MarketListingBox(BaseModel, list):
    def __init__(self):
        super().__init__()
        self.app_data = None  # type: dict
        self.start = None  # type: int
        self.pagesize = None  # type: int
        self.total_count = None  # type: int

    @staticmethod
    def create(json_dict: dict) -> "MarketListingBox":
        mlb = MarketListingBox()
        mlb.app_data = json_dict["app_data"]
        mlb.total_count = json_dict["total_count"]
        mlb.pagesize = int(json_dict["pagesize"])
        mlb.start = json_dict["start"]

        assets_map = utils.get_assets_map(json_dict["assets"])
        for listing_id, listing in json_dict["listinginfo"].items():
            app_id = listing["asset"]["appid"]
            context_id = listing["asset"]["contextid"]
            asset_id = listing["asset"]["id"]
            asset = assets_map.get((str(app_id), context_id, asset_id))
            market_listing = MarketListing.create(listing, asset)
            mlb.append(market_listing)

        return mlb

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = ["success", "total_count", "listinginfo", "assets", "pagesize", "start",
                  "app_data"]

        for field in fields:
            if field not in json_dict:
                return False

        if not json_dict["success"]:
            return False

        return True


class MarketListing(BaseModel):

    def __init__(self):
        self.listing_id = None  # type: str
        self.price = None  # type: int
        self.fee = None  # type: int
        self.publisher_fee_app = None  # type: str
        self.publisher_fee_percent = None  # type: str
        self.currencyid = None  # type: int
        self.steam_fee = None  # type: int
        self.publisher_fee = None  # type: int
        self.converted_price = None  # type: int
        self.converted_fee = None  # type: int
        self.converted_currencyid = None  # type: int
        self.converted_steam_fee = None  # type: int
        self.converted_publisher_fee = None  # type: int
        self.converted_price_per_unit = None  # type: int
        self.converted_fee_per_unit = None  # type: int
        self.converted_steam_fee_per_unit = None  # type: int
        self.converted_publisher_fee_per_unit = None  # type: int

        self.asset = None  # type: Asset

    def get_cprice(self):
        return self.converted_price + self.converted_fee

    @staticmethod
    def create(json_dict: dict, asset: dict) -> "MarketListing":
        ml = MarketListing()

        ml.listing_id = json_dict["listingid"]
        ml.price = json_dict["price"]
        ml.fee = json_dict["fee"]
        ml.publisher_fee_app = str(json_dict["publisher_fee_app"])
        ml.publisher_fee_percent = json_dict["publisher_fee_percent"]
        ml.currencyid = json_dict["currencyid"]
        ml.steam_fee = json_dict["steam_fee"]
        ml.publisher_fee = json_dict["publisher_fee"]
        ml.converted_price = json_dict["converted_price"]
        ml.converted_fee = json_dict["converted_fee"]
        ml.converted_currencyid = json_dict["converted_currencyid"]
        ml.converted_steam_fee = json_dict["converted_steam_fee"]
        ml.converted_publisher_fee = json_dict["converted_publisher_fee"]
        ml.converted_price_per_unit = json_dict["converted_price_per_unit"]
        ml.converted_fee_per_unit = json_dict["converted_fee_per_unit"]
        ml.converted_steam_fee_per_unit = json_dict["converted_steam_fee_per_unit"]
        ml.converted_publisher_fee_per_unit = json_dict["converted_publisher_fee_per_unit"]

        asset = Asset.create(asset)
        ml.asset = asset
        return ml

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        fields = [
            "listingid", "price", "fee", "publisher_fee_app", "publisher_fee_percent", "currencyid",
            "steam_fee",
            "publisher_fee", "converted_price", "converted_fee", "converted_currencyid",
            "converted_steam_fee",
            "converted_publisher_fee", "converted_price_per_unit", "converted_fee_per_unit",
            "converted_steam_fee_per_unit", "converted_publisher_fee_per_unit"
        ]
        for field in fields:
            if field not in json_dict:
                return False

        return True


class Inventory(BaseModel, list):
    def __init__(self):
        super().__init__()

        self.more_items = None  # type: bool
        self.last_asset_id = None  # type: str
        self.total_inventory_count = None  # type: int

    @staticmethod
    def create(json_dict: dict) -> "Inventory":
        inventory = Inventory()
        inventory.more_items = bool(json_dict.get("more_items", 0))
        inventory.total_inventory_count = json_dict["total_inventory_count"]
        inventory.last_asset_id = json_dict.get("last_assetid")

        if inventory.total_inventory_count == 0:
            return inventory

        descriptions = {}
        for descr in json_dict.get("descriptions", []):
            key = (str(descr["appid"]), str(descr["classid"]), str(descr.get("instanceid", "0")))
            descriptions[key] = descr

        for raw_asset in json_dict["assets"]:
            description_key = (
                str(raw_asset["appid"]), str(raw_asset["classid"]),
                str(raw_asset.get("instanceid", 0)))
            if description_key in descriptions:
                raw_asset.update(descriptions[description_key])
            asset = Asset.create(raw_asset)
            inventory.append(asset)

        return inventory

    @staticmethod
    def is_well_formed(json_dict: dict) -> bool:
        if "total_inventory_count" not in json_dict or json_dict["total_inventory_count"] is None:
            return False

        count = json_dict["total_inventory_count"]
        if count == 0:
            return True

        if "assets" in json_dict:
            for asset in json_dict["assets"]:
                if not Asset.is_well_formed(asset):
                    return False
        else:
            return False

        return True


# todo put this in utils?
def _convert_to_date(date_string: str) -> datetime.date:
    """
    Convert dates like this '3 Mar' to datetime.date
    """
    current_date = datetime.now().date()
    current_year = current_date.year
    new_date = datetime.strptime(date_string + " %s" % current_year, "%d %b %Y").date()

    if current_date < new_date:
        new_date = new_date.replace(year=current_year - 1)

    return new_date

# todo check if the methods in utils can be recycled to do this
def _get_descriptions_map(raw_desc: dict) -> dict:
    descriptions = {}
    for descr in raw_desc:
        key = (str(descr["appid"]), str(descr["classid"]), str(descr.get("instanceid", "0")))
        descriptions[key] = descr

    return descriptions


def _add_descriptions_to_asset(assets: List[Asset], desc_map: dict):
    for asset in assets:
        key = (asset.app_id, asset.class_id, asset.instance_id or "0")
        if key in desc_map:
            asset.update(desc_map[key])
