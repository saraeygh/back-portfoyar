import json
import pandas as pd

from colorama import Fore, Style

from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface
from future_market.models import (
    OptionBaseEquity,
    CONTRACT_CODE,
    SANDOQ_MARKET,
    GAVAHI_MARKET,
    CDC_MARKET,
    ID,
)


OPTION_BASE_EQUITY_SYMBOLS = {
    "لوتوس": "TL",
    "كهربا": "KA",
    "زاگرس": "JZ",
    "سکه": "GC",
    "شمش": "GB",
    "زعفران": "SF",
    "آتی زعفران": "FS",
    "آتی لوتوس": "FE",
    "کهربا 10": "KB",
}

NAME_COL = "name"
COL_MAPPING = "col_mapping"
FILTER_BASE_EQUITIES = "filter"
UNIQUE_IDENTIFIER_COL = "unique_identifier"


def filter_fund_base_equities(all_funds: pd.DataFrame):
    if all_funds.empty:
        return all_funds

    filtered_funds = all_funds[~all_funds["Symbol"].str.contains(r"\d")]

    return filtered_funds


def filter_commodity_base_equities(all_commodity: pd.DataFrame):
    filtered_commodity = all_commodity

    return filtered_commodity


def filter_gold_base_equities(all_gold: pd.DataFrame):
    filtered_gold = all_gold

    return filtered_gold


ORDER_BOOK_COLS = {
    "DemandPrice2": "DemandPrice2",
    "OfferPrice2": "OfferPrice2",
    "DemandVolume2": "DemandVolume2",
    "OfferVolume2": "OfferVolume2",
    "DemandPrice3": "DemandPrice3",
    "OfferPrice3": "OfferPrice3",
    "DemandVolume3": "DemandVolume3",
    "OfferVolume3": "OfferVolume3",
    # "DemandPrice4": "DemandPrice4",
    # "OfferPrice4": "OfferPrice4",
    # "DemandVolume4": "DemandVolume4",
    # "OfferVolume4": "OfferVolume4",
    # "DemandPrice5": "DemandPrice5",
    # "OfferPrice5": "OfferPrice5",
    # "DemandVolume5": "DemandVolume5",
    # "OfferVolume5": "OfferVolume5",
}

BASE_EQUITY_KEYS = {
    SANDOQ_MARKET: {
        NAME_COL: "Name",
        UNIQUE_IDENTIFIER_COL: ID,
        FILTER_BASE_EQUITIES: filter_fund_base_equities,
        COL_MAPPING: {
            "ID": "base_equity_ins_code",
            "Symbol": "base_equity_symbol",
            "Name": "base_equity_name",
            "FinalPrice": "base_equity_close_price",
            "YesterdayPrice": "base_equity_yesterday_price",
            "LastPrice": "base_equity_last_price",
            "Value": "base_equity_value",
            "DemandPrice1": "base_equity_best_buy_price",
            "OfferPrice1": "base_equity_best_sell_price",
            "DemandVolume1": "base_equity_best_buy_volume",
            "OfferVolume1": "base_equity_best_sell_volume",
            "ModifyTime": "base_equity_last_update",
            **ORDER_BOOK_COLS,
        },
    },
    GAVAHI_MARKET: {
        NAME_COL: "Name",
        UNIQUE_IDENTIFIER_COL: ID,
        FILTER_BASE_EQUITIES: filter_commodity_base_equities,
        COL_MAPPING: {
            "ID": "base_equity_ins_code",
            "Symbol": "base_equity_symbol",
            "Name": "base_equity_name",
            "FinalPrice": "base_equity_close_price",
            "YesterdayPrice": "base_equity_yesterday_price",
            "LastPrice": "base_equity_last_price",
            "Value": "base_equity_value",
            "DemandPrice1": "base_equity_best_buy_price",
            "OfferPrice1": "base_equity_best_sell_price",
            "DemandVolume1": "base_equity_best_buy_volume",
            "OfferVolume1": "base_equity_best_sell_volume",
            "ModifyTime": "base_equity_last_update",
            **ORDER_BOOK_COLS,
        },
    },
    CDC_MARKET: {
        NAME_COL: "ContractDescription",
        UNIQUE_IDENTIFIER_COL: CONTRACT_CODE,
        FILTER_BASE_EQUITIES: filter_gold_base_equities,
        COL_MAPPING: {
            "ContractCode": "base_equity_ins_code",
            "CommodityName": "base_equity_symbol",
            "ContractDescription": "base_equity_name",
            "HighTradedPrice": "base_equity_close_price",
            "LastSettlementPrice": "base_equity_yesterday_price",
            "LastTradedPrice": "base_equity_last_price",
            "TradesValue": "base_equity_value",
            "BidPrice1": "base_equity_best_buy_price",
            "AskPrice1": "base_equity_best_sell_price",
            "BidVolume1": "base_equity_best_buy_volume",
            "AskVolume1": "base_equity_best_sell_volume",
            "OrdersPersianDateTime": "base_equity_last_update",
            #
            "BidPrice2": "DemandPrice2",
            "AskPrice2": "OfferPrice2",
            "BidVolume2": "DemandVolume2",
            "AskVolume2": "OfferVolume2",
            "BidPrice3": "DemandPrice3",
            "AskPrice3": "OfferPrice3",
            "BidVolume3": "DemandVolume3",
            "AskVolume3": "OfferVolume3",
            # "BidPrice4": "DemandPrice4",
            # "AskPrice4": "OfferPrice4",
            # "BidVolume4": "DemandVolume4",
            # "AskVolume4": "OfferVolume4",
            # "BidPrice5": "DemandPrice5",
            # "AskPrice5": "OfferPrice5",
            # "BidVolume5": "DemandVolume5",
            # "AskVolume5": "OfferVolume5",
        },
    },
}


def get_options_base_equity_info():
    print(Fore.BLUE + "Updating options base equity info ..." + Style.RESET_ALL)
    base_equities = pd.DataFrame(
        OptionBaseEquity.objects.values(
            "base_equity_key",
            "derivative_symbol",
            "unique_identifier",
        )
    )

    base_equity_data = pd.DataFrame()

    redis_conn = RedisInterface(db=FUTURE_REDIS_DB)
    for base_equity_key, properties in BASE_EQUITY_KEYS.items():
        data = redis_conn.client.get(name=base_equity_key)
        data = json.loads(data.decode("utf-8"))
        data = pd.DataFrame(data)
        data = (properties.get(FILTER_BASE_EQUITIES))(data)

        col_mapping = properties.get(COL_MAPPING)
        data.rename(columns=col_mapping, inplace=True)
        data = data[list(col_mapping.values())]

        base_equity_data = pd.concat([base_equity_data, data])
    redis_conn.client.close()

    base_equities = pd.merge(
        left=base_equities,
        right=base_equity_data,
        left_on="unique_identifier",
        right_on="base_equity_ins_code",
        how="left",
    )

    return base_equities
