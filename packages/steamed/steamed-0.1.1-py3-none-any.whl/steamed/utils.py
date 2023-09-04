import urllib.parse as urlparse
from typing import Union, Tuple, Dict

import requests

from steampye.exceptions import TooManyRequests, SteamServerError


def text_between(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]


def texts_between(text: str, begin: str, end: str):
    stop = 0
    while True:
        try:
            start = text.index(begin, stop) + len(begin)
            stop = text.index(end, start)
            yield text[start:stop]
        except Exception as e:  # todo fix too broad
            return


def account_id_to_steam_id(account_id: str) -> str:
    if int(account_id) > 76561197960265728:
        return account_id
    return str(int(account_id) + 76561197960265728)


def steam_id_to_account_id(steam_id: str) -> str:
    if int(steam_id) < 76561197960265728:
        return steam_id
    return str(int(steam_id) - 76561197960265728)


def price_to_float(price: str) -> float:
    return float(price[1:].split()[0])


def get_assets_map(assets: dict) -> Dict[Tuple[str, str, str], dict]:
    amap = {}
    for appid in assets.keys():
        for contextid in assets[appid].keys():
            for assetid, asset in assets[appid][contextid].items():
                amap[(str(appid), str(contextid), str(assetid))] = asset
    return amap

def map_asset_to_descriptions(assets, descriptions):
    map_desc = {}
    for desc in descriptions:
        key = (desc["appid"], desc["classid"], desc["instanceid"])
        map_desc[key] = desc

    mapp = {}
    for asset in assets:
        key = (asset["appid"], asset["classid"], asset["instanceid"])
        if key not in map_desc:
            raise KeyError(f"Cannot associate the asset {asset} with a description. Descriptions map: {map_desc}")
        mapp[asset["assetid"]] = map_desc[key]
    return mapp


def get_token_from_trade_offer_url(trade_offer_url: str) -> str:
    params = urlparse.urlparse(trade_offer_url).query
    return urlparse.parse_qs(params)["token"][0]


def get_partner_from_trade_offer_url(trade_offer_url: str) -> str:
    params = urlparse.urlparse(trade_offer_url).query
    return urlparse.parse_qs(params)["partner"][0]


def extract_json(response: requests.Response) -> dict:
    try:
        json_response = response.json()
    except ValueError as e:
        raise SteamServerError("Invalid Json") from e

    if "response" in json_response:
        json_response = json_response["response"]

    return json_response


def normalize_price(price: str) -> Union[int, str]:
    try:
        price = price.replace("--", "00").replace(",", ".").replace(" ", "")
        if price[-1] not in "0123456789":
            price = price[:-1]
        return round(float(price) * 100)
    except Exception as e:
        raise ValueError("Wrong Price: %s" % price) from e