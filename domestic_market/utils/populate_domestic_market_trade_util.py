import json
from datetime import datetime, timedelta

from tqdm import tqdm
import jdatetime as jdt


from core.utils import get_http_response, get_deviation_percent

from domestic_market.models import (
    DomesticCommodity,
    DomesticProducer,
    DomesticTrade,
    DomesticTradesHistoryFetch,
)

TRADES_HISTORY_TIME_PERIOD = 90
FIRST_TRADE_DATE_STR = "1380/01/01"

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

URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"


def get_date_str_from_gregorian(date_obj):
    return jdt.date.fromgregorian(date=date_obj, locale="fa_IR").strftime("%Y/%m/%d")


def get_gregorian_trade_obj(date_str):
    year, month, day = map(int, date_str.split("/"))
    return jdt.date(year=year, month=month, day=day).togregorian()


def get_producer(producer_name):
    producer = DomesticProducer.objects.filter(name=producer_name)
    if producer.count() == 0:
        return None
    if producer.count() == 1:
        return producer.first()
    else:
        return producer.order_by("code").last()


def last_trade_date():
    last_trade = DomesticTrade.objects.order_by("trade_date").last()
    if last_trade:
        return last_trade.trade_date

    return None


def get_trades_between_dates(start_date: str, end_date: str):
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

    print(
        f"Getting trades data ({start_date} to {end_date}) ...",
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
        start_obj = jdt.date(year=year, month=month, day=day)
        start_str = start_obj.strftime("%Y/%m/%d")

        end_obj = start_obj + jdt.timedelta(days=TRADES_HISTORY_TIME_PERIOD)
        end_str = end_obj.strftime("%Y/%m/%d")

        return get_trades_between_dates(start_date=start_str, end_date=end_str)

    return trade_list_of_dict


def populate_trades_between_dates(start_date: str, end_date: str):
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

    trades_bulk_list = []
    for trade in tqdm(
        trades_list_of_dict, desc=f"Domestic {start_date} to {end_date}", ncols=10
    ):
        if trade["Quantity"] <= 0:
            continue

        _, _, commodity_code = map(int, trade.get("Category").split("-"))
        try:
            commodity = DomesticCommodity.objects.get(code=commodity_code)
        except DomesticCommodity.DoesNotExist:
            continue

        producer = get_producer(trade["ProducerName"])
        if producer is None:
            continue

        trade_date = get_gregorian_trade_obj(trade.get("date"))

        try:
            delivery_date = get_gregorian_trade_obj(trade.get("DeliveryDate"))
        except Exception:
            delivery_date = get_gregorian_trade_obj(trade.get("date"))

        base_price = trade.get("ArzeBasePrice")
        close_price = trade.get("Price")
        if base_price == 0:
            competition = 0
        else:
            competition = get_deviation_percent(close_price, base_price)

        new_trade = {
            "commodity": commodity,
            "producer": producer,
            "trade_date": trade_date,
            "delivery_date": delivery_date,
            "base_price": base_price,
            "close_price": close_price,
            "competition": competition,
            "trade_date_shamsi": trade.get("date"),
            "commodity_name": trade.get("GoodsName"),
            "symbol": trade.get("Symbol"),
            "contract_type": trade.get("ContractType"),
            "value": trade.get("TotalPrice"),
            "currency": trade.get("Currency"),
            "unit": trade.get("Unit"),
            "min_price": trade.get("MinPrice"),
            "max_price": trade.get("MaxPrice"),
            "supply_volume": trade.get("arze"),
            "demand_volume": trade.get("taghaza"),
            "contract_volume": trade.get("Quantity"),
            "broker": trade.get("cBrokerSpcName"),
            "delivery_date_shamsi": trade.get("DeliveryDate"),
            "supply_pk": trade.get("arzehPk"),
        }

        try:
            DomesticTrade.objects.get(**new_trade)
        except DomesticTrade.DoesNotExist:
            new_trade_obj = DomesticTrade(**new_trade)
            trades_bulk_list.append(new_trade_obj)

    if trades_bulk_list:
        bulk_created_list = DomesticTrade.objects.bulk_create(trades_bulk_list)

        new_trade_history.db_populated = True
        new_trade_history.number_of_populated_trades = len(bulk_created_list)
        new_trade_history.save()
        print(
            f"Populated trades from {start_date} to {end_date}, {len(trades_bulk_list)} records."
        )


def populate_domestic_market_trade():
    today_date_obj = datetime.today().date()
    last_date_obj = last_trade_date()

    if last_date_obj is None:
        start_str = FIRST_TRADE_DATE_STR
        last_date_obj = get_gregorian_trade_obj(start_str)
    else:
        start_str = get_date_str_from_gregorian(last_date_obj)

    end_str = get_date_str_from_gregorian(today_date_obj)

    trade_history_duration = (today_date_obj - last_date_obj).days
    if 0 <= trade_history_duration < TRADES_HISTORY_TIME_PERIOD:
        populate_trades_between_dates(start_date=start_str, end_date=end_str)

    else:
        iter_num = (trade_history_duration // TRADES_HISTORY_TIME_PERIOD) + 1
        start_obj = last_date_obj
        for _ in range(iter_num):
            end_obj = start_obj + timedelta(days=TRADES_HISTORY_TIME_PERIOD)

            start_str = get_date_str_from_gregorian(start_obj)
            end_str = get_date_str_from_gregorian(end_obj)

            populate_trades_between_dates(start_date=start_str, end_date=end_str)

            start_obj = end_obj
