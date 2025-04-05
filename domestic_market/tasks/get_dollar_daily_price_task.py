import random
from datetime import datetime
import jdatetime

from bs4 import BeautifulSoup

from core.utils import run_main_task, get_http_response
from domestic_market.models import DomesticDollarPrice


def get_last_dollar_price():
    return DomesticDollarPrice.objects.last()


TGJU_API_LIST = [1, 2, 3, 4]


def update_azad_price(last_dollar, today_price_date):
    TGJU_MAIN_URL = f"https://call{random.choice(TGJU_API_LIST)}.tgju.org/ajax.json"
    response = get_http_response(req_url=TGJU_MAIN_URL)
    response = response.json()
    lasts = response.get("last")

    for last_item in lasts:
        name = last_item.get("name")
        if name == "price_dollar_rl":
            last_price_value = last_item.get("p")
            last_price_value = int((last_price_value).replace(",", ""))
            try:
                last_dollar_price = DomesticDollarPrice.objects.get(
                    date=today_price_date
                )
                last_dollar_price.azad = last_price_value
                last_dollar_price.save()
            except DomesticDollarPrice.DoesNotExist:
                today_price_date_shamsi = str(
                    jdatetime.date.fromgregorian(date=today_price_date)
                )

                DomesticDollarPrice.objects.create(
                    date=today_price_date,
                    date_shamsi=today_price_date_shamsi,
                    azad=last_price_value,
                    nima=last_dollar.nima,
                )


def get_dollar_price_bs(URL: str):

    response = get_http_response(req_url=URL)
    response = response.text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find_all("td")

    for index, td in enumerate(soup):
        if td.string == "نرخ فعلی":
            last_price_value = soup[index + 1]
            break

    last_price_value = int((last_price_value.string).replace(",", ""))

    return last_price_value


def update_nima_price(last_dollar, today_price_date):
    NIMA_URL = "https://www.tgju.org/profile/nima_sell_usd"
    nima_usd_price = get_dollar_price_bs(URL=NIMA_URL)

    try:
        last_dollar_price = DomesticDollarPrice.objects.get(date=today_price_date)
        last_dollar_price.nima = nima_usd_price
        last_dollar_price.save()
    except DomesticDollarPrice.DoesNotExist:
        today_price_date_shamsi = str(
            jdatetime.date.fromgregorian(date=today_price_date)
        )

        DomesticDollarPrice.objects.create(
            date=today_price_date,
            date_shamsi=today_price_date_shamsi,
            azad=last_dollar.azad,
            nima=nima_usd_price,
        )


def get_dollar_daily_price_main():

    last_dollar = get_last_dollar_price()
    today_price_date = datetime.now().date()

    update_azad_price(last_dollar, today_price_date)
    update_nima_price(last_dollar, today_price_date)


def get_dollar_daily_price():

    run_main_task(
        main_task=get_dollar_daily_price_main,
    )
