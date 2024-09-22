from datetime import datetime

import jdatetime
from tqdm import tqdm
from core.utils import task_timing, get_http_response
from domestic_market.models import DomesticDollarPrice, BourseViewCookie
from domestic_market.utils import get_existing_dollar_prices_dict


def get_last_dollar_price(dollar: str):
    if dollar == "azad":
        last_usd_price = DomesticDollarPrice.objects.last().azad
    elif dollar == "nima":
        last_usd_price = DomesticDollarPrice.objects.last().nima

    return last_usd_price


def get_dollar_price_dict(URL: str):

    cookie = BourseViewCookie.objects.first().cookie
    HEADERS = {
        "Host": "www.bourseview.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Language": "FA",
        "Connection": "keep-alive",
        "Referer": "https://www.bourseview.com/home/",
        "Cookie": f"{cookie}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    dollar_price_dict = {}
    response = get_http_response(req_url=URL, req_headers=HEADERS)

    try:
        prices = (response.json())["items"]
    except Exception:
        return dollar_price_dict

    for price in prices:
        try:
            price_value = int(price["value"])
            price_date = str(price["periodEndingDate"])
            price_date = datetime.strptime(price_date, "%Y%m%d").date()
            dollar_price_dict[price_date] = price_value
        except Exception:
            continue

    return dollar_price_dict


@task_timing
def get_dollar_price_history():
    AZAD_URL = "https://www.bourseview.com/api/v2/currency?fromTo=[107,106]"
    NIMA_URL = "https://www.bourseview.com/api/v2/currency?fromTo=[100,106]"

    azad_usd_price_dict = get_dollar_price_dict(URL=AZAD_URL)
    nima_usd_price_dict = get_dollar_price_dict(URL=NIMA_URL)

    azad_usd_price_dates = set(azad_usd_price_dict.keys())
    nima_usd_price_dates = set(nima_usd_price_dict.keys())
    common_dates = azad_usd_price_dates & nima_usd_price_dates
    common_dates = list(common_dates)
    common_dates.sort()

    existing_dollar_prices_dict = get_existing_dollar_prices_dict()
    if not existing_dollar_prices_dict:
        first_price_date = datetime(year=2001, month=3, day=25).date()
        first_dollar_price = DomesticDollarPrice.objects.create(
            date=first_price_date,
            date_shamsi="1380-01-05",
            azad=8028,
            nima=8028,
        )
        existing_dollar_prices_dict[first_price_date] = first_dollar_price

    bulk_create_dollar_price_list = []
    for price_date in tqdm(common_dates, desc="Getting dollar price history", ncols=10):
        azad_price = azad_usd_price_dict.get(price_date)
        if not azad_price:
            azad_price = get_last_dollar_price(dollar="azad")

        nima_price = nima_usd_price_dict.get(price_date)
        if not nima_price:
            nima_price = get_last_dollar_price(dollar="nima")

        if price_date in existing_dollar_prices_dict:
            continue
        else:
            new_price = DomesticDollarPrice(
                date=price_date,
                date_shamsi=str(jdatetime.date.fromgregorian(date=price_date)),
                azad=azad_price,
                nima=nima_price,
            )
            bulk_create_dollar_price_list.append(new_price)
            existing_dollar_prices_dict[price_date] = new_price

    if bulk_create_dollar_price_list:
        DomesticDollarPrice.objects.bulk_create(bulk_create_dollar_price_list)
