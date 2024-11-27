import json
import pandas as pd
import jdatetime

from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface

from future_market.models import OPTION_INFO
from future_market.utils import (
    get_options_base_equity_info,
    OPTION_COLUMNS,
    populate_all_strategy,
)

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)

REPLACE_SYMBOL_DICT = {
    "قرارداد اختیار معامله فروش ": "ا.ف ",
    "قرارداد اختیار معامله خرید": "ا.خ ",
    "سررسید": "",
    "ریال": "",
    "با قیمت اعمال": "",
    "مبتنی بر قرارداد": "",
    "ماه": "",
    "واحدهای سرمایه گذاری صندوق طلای": "",
    "صندوق طلای": "",
    "  ": " ",
}


TSE_ORDER_BOOK = {
    "n": "row",
    # BUY
    "qmd": "buy_volume",
    "pmd": "buy_price",
    # SELL
    "qmo": "sell_volume",
    "pmo": "sell_price",
}


def add_call_order_book(row):
    call_order_book = [
        {
            "row": 1,
            "buy_volume": row.get("CallBidVolume1"),
            "buy_price": row.get("CallBidPrice1"),
            "sell_volume": row.get("CallAskVolume1"),
            "sell_price": row.get("CallAskPrice1"),
        },
        {
            "row": 2,
            "buy_volume": row.get("CallBidVolume2"),
            "buy_price": row.get("CallBidPrice2"),
            "sell_volume": row.get("CallAskVolume2"),
            "sell_price": row.get("CallAskPrice2"),
        },
        {
            "row": 3,
            "buy_volume": row.get("CallBidVolume3"),
            "buy_price": row.get("CallBidPrice3"),
            "sell_volume": row.get("CallAskVolume3"),
            "sell_price": row.get("CallAskPrice3"),
        },
        {
            "row": 4,
            "buy_volume": row.get("CallBidVolume4"),
            "buy_price": row.get("CallBidPrice4"),
            "sell_volume": row.get("CallAskVolume4"),
            "sell_price": row.get("CallAskPrice4"),
        },
        {
            "row": 5,
            "buy_volume": row.get("CallBidVolume5"),
            "buy_price": row.get("CallBidPrice5"),
            "sell_volume": row.get("CallAskVolume5"),
            "sell_price": row.get("CallAskPrice5"),
        },
    ]

    return call_order_book


def add_put_order_book(row):
    put_order_book = [
        {
            "row": 1,
            "buy_volume": row.get("PutBidVolume1"),
            "buy_price": row.get("PutBidPrice1"),
            "sell_volume": row.get("PutAskVolume1"),
            "sell_price": row.get("PutAskPrice1"),
        },
        {
            "row": 2,
            "buy_volume": row.get("PutBidVolume2"),
            "buy_price": row.get("PutBidPrice2"),
            "sell_volume": row.get("PutAskVolume2"),
            "sell_price": row.get("PutAskPrice2"),
        },
        {
            "row": 3,
            "buy_volume": row.get("PutBidVolume3"),
            "buy_price": row.get("PutBidPrice3"),
            "sell_volume": row.get("PutAskVolume3"),
            "sell_price": row.get("PutAskPrice3"),
        },
        {
            "row": 4,
            "buy_volume": row.get("PutBidVolume4"),
            "buy_price": row.get("PutBidPrice4"),
            "sell_volume": row.get("PutAskVolume4"),
            "sell_price": row.get("PutAskPrice4"),
        },
        {
            "row": 5,
            "buy_volume": row.get("PutBidVolume5"),
            "buy_price": row.get("PutBidPrice5"),
            "sell_volume": row.get("PutAskVolume5"),
            "sell_price": row.get("PutAskPrice5"),
        },
    ]

    return put_order_book


def add_base_equity_order_book(row):
    put_order_book = [
        {
            "row": 1,
            "buy_volume": row.get("base_equity_best_buy_volume"),
            "buy_price": row.get("base_equity_best_buy_price"),
            "sell_volume": row.get("base_equity_best_sell_volume"),
            "sell_price": row.get("base_equity_best_sell_price"),
        },
        {
            "row": 2,
            "buy_volume": row.get("DemandVolume2"),
            "buy_price": row.get("DemandPrice2"),
            "sell_volume": row.get("OfferVolume2"),
            "sell_price": row.get("OfferPrice2"),
        },
        {
            "row": 3,
            "buy_volume": row.get("DemandVolume3"),
            "buy_price": row.get("DemandPrice3"),
            "sell_volume": row.get("OfferVolume3"),
            "sell_price": row.get("OfferPrice3"),
        },
        {
            "row": 4,
            "buy_volume": row.get("DemandVolume4"),
            "buy_price": row.get("DemandPrice4"),
            "sell_volume": row.get("OfferVolume4"),
            "sell_price": row.get("OfferPrice4"),
        },
        {
            "row": 5,
            "buy_volume": row.get("DemandVolume5"),
            "buy_price": row.get("DemandPrice5"),
            "sell_volume": row.get("OfferVolume5"),
            "sell_price": row.get("OfferPrice5"),
        },
    ]

    return put_order_book


def add_symbol_to_option_data(row):
    contract_code = str(row.get("CallContractCode"))
    symbol = contract_code[0:2]
    return symbol


def add_remained_day(row):
    end_date = str(row.get("end_date"))
    year, month, day = end_date.split("/")
    year, month, day = int(year), int(month), int(day)
    end_date = jdatetime.date(year=year, month=month, day=day)
    today_date = jdatetime.date.today()
    remained_day = (end_date - today_date).days

    return remained_day


def change_str_last_update_to_int(row, col_name):
    try:
        last_update = str(row.get(col_name))
        last_update = int((last_update.split(" - ")[1]).replace(":", ""))
        return last_update
    except Exception:
        pass

    try:
        last_update = str(row.get(col_name))
        last_update = int(last_update.replace(":", ""))
    except Exception:
        last_update = 0

    return last_update


def shorten_option_symbol(row, col_name):
    try:
        shortened_option_symbol = str(row.get(col_name))
        for to_replace, replacement in REPLACE_SYMBOL_DICT.items():
            shortened_option_symbol = shortened_option_symbol.replace(
                to_replace, replacement
            )
        return shortened_option_symbol
    except Exception:
        return str(row.get(col_name))


def update_option_result_main():
    option_data = json.loads(redis_conn.client.get(name=OPTION_INFO))
    option_data = pd.DataFrame(option_data)

    option_data["call_order_book"] = option_data.apply(add_call_order_book, axis=1)
    option_data["put_order_book"] = option_data.apply(add_put_order_book, axis=1)

    option_data["symbol"] = option_data.apply(add_symbol_to_option_data, axis=1)
    base_equity_data = get_options_base_equity_info()
    base_equity_data["base_equity_order_book"] = base_equity_data.apply(
        add_base_equity_order_book, axis=1
    )
    option_data = pd.merge(
        left=option_data, right=base_equity_data, on="symbol", how="left"
    )

    option_data.rename(columns=OPTION_COLUMNS, inplace=True)
    option_data = option_data[list(OPTION_COLUMNS.values())]
    option_data["remained_day"] = option_data.apply(add_remained_day, axis=1)

    option_data["call_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("call_last_update",)
    )

    option_data["put_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("put_last_update",)
    )

    option_data["base_equity_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("base_equity_last_update",)
    )

    option_data["call_symbol"] = option_data.apply(
        shorten_option_symbol, axis=1, args=("call_symbol",)
    )
    option_data["put_symbol"] = option_data.apply(
        shorten_option_symbol, axis=1, args=("put_symbol",)
    )
    populate_all_strategy(option_data)


def update_option_result():
    update_option_result_main()
