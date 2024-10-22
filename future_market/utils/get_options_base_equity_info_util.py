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

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


OPTION_BASE_EQUITY_SYMBOLS = {
    # "زعفران": "SAF",
    # "لوتوس": "ETC",
    # "شمش": "GB",
    # "كهربا": "KB",
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
        },
    },
}

TO_BE_DELETED = ["51200575796028449"]


def get_options_base_equity_info():
    print("Updating options base equity info ...")
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
                print(e)
                continue
    print("All options base equity info updated")

    print("Deleting mistaken base equities ...")
    corrected_options_base_equity = list()
    for base_equity in base_equity_list:
        base_equity_ins_code = base_equity.get("base_equity_ins_code")
        if base_equity_ins_code in TO_BE_DELETED:
            continue
        corrected_options_base_equity.append(base_equity)
    print("Mistaken base equities deleted")
    corrected_options_base_equity = pd.DataFrame(corrected_options_base_equity)

    return corrected_options_base_equity
