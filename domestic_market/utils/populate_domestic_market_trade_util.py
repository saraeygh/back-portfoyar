from difflib import SequenceMatcher
import json
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import jdatetime
import pandas as pd
from domestic_market.models import (
    DomesticCommodity,
    DomesticProducer,
    DomesticTrade,
    DomesticTradesHistoryFetch,
)
from core.utils import get_http_response
from colorama import Fore, Style

TRADES_HISTORY_TIME_PERIOD = 90
FIRST_TRADE_DATE_STR = "1380/01/01"


def get_producer_id(producer_name, producer_names_list):
    ratios = []
    for name in producer_names_list:
        ratio = SequenceMatcher(None, producer_name, name).ratio()
        ratios.append(ratio)

    max_ratio = max(ratios)
    max_ratio_index = ratios.index(max_ratio)
    matched_name = producer_names_list[max_ratio_index]

    producer_id = DomesticProducer.objects.filter(name=matched_name).first().id

    return producer_id


def last_trade_date():
    return (
        DomesticTrade.objects.order_by("trade_date")
        .values_list("trade_date", flat=True)
        .last()
    )


def get_trades_between_dates(start_date: str, end_date: str):
    HEADERS = {
        "Host": "www.ime.co.ir",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Length": "119",
        "Origin": "https://www.ime.co.ir",
        "Connection": "keep-alive",
        "Referer": "https://www.ime.co.ir/offer-stat.html",
        "Cookie": "ASP.NET_SessionId=zebwrt1sbsuvpw30ze4wgub3; SiteBikeLoadBanacer=9609d25e7d6e5b16cafdd45c3cf1d1ebdb204366ac7135985c4cd71dffa8dd38",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    PAYLOAD = {
        "Language": 8,
        "fari": "false",
        "GregorianFromDate": start_date,
        "GregorianToDate": end_date,
        "MainCat": 0,
        "Cat": 0,
        "SubCat": 0,
        "Producer": 0,
    }

    URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"

    print(
        Fore.BLUE
        + f"Getting trades data ({start_date} to {end_date}) ..."
        + Style.RESET_ALL,
        end="\r",
    )
    response = get_http_response(
        req_method="POST", req_url=URL, req_json=PAYLOAD, req_headers=HEADERS
    )

    try:
        trade = response.content.decode()
        trade = json.loads(trade)
        trade = trade.get("d")
        trade_list_of_dict = json.loads(trade)

    except Exception:
        year, month, day = map(int, end_date.split("/"))
        start_date_obj = jdatetime.date(year=year, month=month, day=day)
        start_date_str = str(start_date_obj).replace("-", "/")

        end_date_obj = start_date_obj + jdatetime.timedelta(
            days=TRADES_HISTORY_TIME_PERIOD
        )
        end_date_str = str(end_date_obj).replace("-", "/")

        return get_trades_between_dates(
            start_date=start_date_str, end_date=end_date_str
        )

    return trade_list_of_dict


def populate_trades_between_dates(start_date: str, end_date: str, producer_names: list):
    new_trade_history = DomesticTradesHistoryFetch(
        start_date=start_date, end_date=end_date, request_sent=True
    )
    new_trade_history.save()

    trades_list_of_dict = get_trades_between_dates(
        start_date=start_date, end_date=end_date
    )

    new_trade_history.received_trades = True
    new_trade_history.number_of_trades_received = len(trades_list_of_dict)
    new_trade_history.start_populating_db = True
    new_trade_history.save()

    trades_list_of_dict_df = pd.DataFrame(trades_list_of_dict)
    if trades_list_of_dict_df.empty:
        trades_list_of_dict_df = []
    else:

        trades_list_of_dict_df = trades_list_of_dict_df[
            trades_list_of_dict_df["Quantity"] != 0
        ]
        trades_list_of_dict = trades_list_of_dict_df.to_dict(orient="records")

    trades_bulk_list = []
    for trade in tqdm(
        trades_list_of_dict,
        desc=f"Domestic {start_date} to {end_date}",
        ncols=10,
    ):
        _, _, commodity_code = map(int, trade.get("Category").split("-"))
        if DomesticCommodity.objects.filter(code=commodity_code).exists():
            commodity_id = (
                DomesticCommodity.objects.filter(code=commodity_code).first().id
            )
        else:
            continue

        producer_name = trade.get("ProducerName")
        producer_id = get_producer_id(
            producer_name=producer_name, producer_names_list=producer_names
        )

        year, month, day = map(int, trade.get("date").split("/"))
        trade_date = jdatetime.date(year=year, month=month, day=day).togregorian()

        try:
            year, month, day = map(int, trade.get("DeliveryDate").split("/"))
        except Exception as e:
            print(Fore.RED + e + Style.RESET_ALL)
            continue
        delivery_date = jdatetime.date(year=year, month=month, day=day).togregorian()

        base_price = trade.get("ArzeBasePrice")
        close_price = trade.get("Price")
        if base_price == 0:
            competition = 0
        else:
            competition = ((close_price / base_price) - 1) * 100

        new_trade = DomesticTrade(
            commodity_id=commodity_id,
            producer_id=producer_id,
            trade_date=trade_date,
            delivery_date=delivery_date,
            base_price=base_price,
            close_price=close_price,
            competition=competition,
            trade_date_shamsi=trade.get("date"),
            commodity_name=trade.get("GoodsName"),
            symbol=trade.get("Symbol"),
            contract_type=trade.get("ContractType"),
            value=trade.get("TotalPrice"),
            currency=trade.get("Currency"),
            unit=trade.get("Unit"),
            min_price=trade.get("MinPrice"),
            max_price=trade.get("MaxPrice"),
            supply_volume=trade.get("arze"),
            demand_volume=trade.get("taghaza"),
            contract_volume=trade.get("Quantity"),
            broker=trade.get("cBrokerSpcName"),
            delivery_date_shamsi=trade.get("DeliveryDate"),
        )

        trades_bulk_list.append(new_trade)

    if trades_bulk_list:
        bulk_created_list = DomesticTrade.objects.bulk_create(trades_bulk_list)

        new_trade_history.db_populated = True
        new_trade_history.number_of_populated_trades = len(bulk_created_list)
        new_trade_history.save()
        print(
            Fore.BLUE
            + f"Populated trades from {start_date} to {end_date}, {len(trades_bulk_list)} records."
            + Style.RESET_ALL
        )


def populate_domestic_market_trade():
    db_producer_names = DomesticProducer.objects.all().values("name")
    db_producer_names = [producer_name["name"] for producer_name in db_producer_names]

    today_date_obj = datetime.today().date()

    last_date_obj = last_trade_date()
    if last_date_obj is None:
        start_date_str = FIRST_TRADE_DATE_STR
        year, month, day = map(int, start_date_str.split("/"))
        last_date_obj = jdatetime.date(year=year, month=month, day=day).togregorian()
    else:
        start_date_str = str(
            jdatetime.date.fromgregorian(date=last_date_obj, locale="fa_IR")
        ).replace("-", "/")

    end_date_str = str(
        jdatetime.date.fromgregorian(date=today_date_obj, locale="fa_IR")
    ).replace("-", "/")

    if (
        timedelta(days=0)
        <= today_date_obj - last_date_obj
        < timedelta(days=TRADES_HISTORY_TIME_PERIOD)
    ):
        populate_trades_between_dates(
            start_date=start_date_str,
            end_date=end_date_str,
            producer_names=db_producer_names,
        )

    else:
        iter_num = (
            ((today_date_obj - last_date_obj).days) // TRADES_HISTORY_TIME_PERIOD
        ) + 1
        start_date_obj = last_date_obj
        for _ in range(iter_num):
            end_date_obj = start_date_obj + timedelta(days=TRADES_HISTORY_TIME_PERIOD)

            start_date_str = str(
                jdatetime.date.fromgregorian(date=start_date_obj, locale="fa_IR")
            ).replace("-", "/")

            end_date_str = str(
                jdatetime.date.fromgregorian(date=end_date_obj, locale="fa_IR")
            ).replace("-", "/")

            populate_trades_between_dates(
                start_date=start_date_str,
                end_date=end_date_str,
                producer_names=db_producer_names,
            )

            start_date_obj = end_date_obj
