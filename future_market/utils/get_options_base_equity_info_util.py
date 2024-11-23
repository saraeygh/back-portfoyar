import json
import pandas as pd
from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface
from future_market.models import (
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
)
from colorama import Fore, Style

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


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
    filtered_funds = all_funds[~all_funds["Symbol"].str.contains(r"\d")]
    filtered_funds = filtered_funds.to_dict(orient="records")

    return filtered_funds


def filter_commodity_base_equities(all_commodity: pd.DataFrame):
    filtered_commodity = all_commodity
    filtered_commodity = filtered_commodity.to_dict(orient="records")
    return filtered_commodity


def filter_gold_base_equities(all_gold: pd.DataFrame):
    filtered_gold = all_gold
    filtered_gold = filtered_gold.to_dict(orient="records")
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
    "DemandPrice4": "DemandPrice4",
    "OfferPrice4": "OfferPrice4",
    "DemandVolume4": "DemandVolume4",
    "OfferVolume4": "OfferVolume4",
    "DemandPrice5": "DemandPrice5",
    "OfferPrice5": "OfferPrice5",
    "DemandVolume5": "DemandVolume5",
    "OfferVolume5": "OfferVolume5",
}

BASE_EQUITY_KEYS = {
    FUND_INFO: {
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
    COMMODITY_INFO: {
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
    GOLD_INFO: {
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
            "BidPrice4": "DemandPrice4",
            "AskPrice4": "OfferPrice4",
            "BidVolume4": "DemandVolume4",
            "AskVolume4": "OfferVolume4",
            "BidPrice5": "DemandPrice5",
            "AskPrice5": "OfferPrice5",
            "BidVolume5": "DemandVolume5",
            "AskVolume5": "OfferVolume5",
        },
    },
}

TO_BE_DELETED = ["51200575796028449"]

MISSING_BASE_EQUITIES = {
    "46700660505281786": "FE",
    "25559236668122210": "KB",
}


def add_missing_base_equities_symbols(options_base_equity: pd.DataFrame):
    missing_base_equity_list = list()
    for base_equity_ins_code, symbol in MISSING_BASE_EQUITIES.items():
        row = options_base_equity.loc[
            options_base_equity["base_equity_ins_code"] == base_equity_ins_code
        ]

        try:
            row = row.to_dict(orient="records")[0]
        except Exception:
            continue

        row["symbol"] = symbol
        missing_base_equity_list.append(row)

    missing_base_equity_df = pd.DataFrame(missing_base_equity_list)

    sf_base_equities = options_base_equity[options_base_equity["symbol"] == "SF"]
    sf_base_equities["symbol"] = "FS"

    options_base_equity = pd.concat(
        [options_base_equity, missing_base_equity_df, sf_base_equities]
    )

    return options_base_equity


def get_options_base_equity_info():
    print(Fore.BLUE + "Updating options base equity info ..." + Style.RESET_ALL)
    base_equity_list = list()
    for name, symbol in OPTION_BASE_EQUITY_SYMBOLS.items():
        for base_equity_key, properties in BASE_EQUITY_KEYS.items():
            try:
                data = redis_conn.client.get(name=base_equity_key)
                data = json.loads(data.decode("utf-8"))
                data = pd.DataFrame(data)
                data = (properties.get(FILTER_BASE_EQUITIES))(data)
                for datum in data:
                    base_equity_name = datum.get(properties.get(NAME_COL))
                    if name in base_equity_name:
                        col_mapping = properties.get(COL_MAPPING)
                        base_equity_data = dict()
                        for old_col, new_col in col_mapping.items():
                            base_equity_data[new_col] = datum.get(old_col)
                        base_equity_data["symbol"] = symbol
                        base_equity_list.append(base_equity_data)

            except Exception as e:
                print(Fore.RED)
                print(e)
                print(Style.RESET_ALL)
                continue
    print(Fore.GREEN + "All options base equity info updated" + Style.RESET_ALL)

    print(Fore.BLUE + "Deleting mistaken base equities ..." + Style.RESET_ALL)
    corrected_options_base_equity = list()
    for base_equity in base_equity_list:
        base_equity_ins_code = base_equity.get("base_equity_ins_code")
        if base_equity_ins_code in TO_BE_DELETED:
            continue
        corrected_options_base_equity.append(base_equity)
    print(Fore.GREEN + "Mistaken base equities deleted" + Style.RESET_ALL)
    corrected_options_base_equity = pd.DataFrame(corrected_options_base_equity)

    corrected_options_base_equity = corrected_options_base_equity.drop_duplicates(
        subset="base_equity_ins_code", keep=False
    )

    corrected_options_base_equity = add_missing_base_equities_symbols(
        corrected_options_base_equity
    )

    return corrected_options_base_equity
