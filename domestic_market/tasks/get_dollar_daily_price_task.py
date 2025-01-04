from datetime import datetime
import jdatetime

from bs4 import BeautifulSoup

from core.utils import run_main_task, get_http_response
from domestic_market.models import DomesticDollarPrice
from domestic_market.utils import get_existing_dollar_prices_dict


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


def get_dollar_daily_price_main():
    AZAD_URL = "https://www.tgju.org/profile/price_dollar_rl"
    NIMA_URL = "https://www.tgju.org/profile/nima_sell_usd"

    azad_usd_price = get_dollar_price_bs(URL=AZAD_URL)
    nima_usd_price = get_dollar_price_bs(URL=NIMA_URL)

    today_price_date = datetime.now().date()
    existing_dollar_prices_dict = get_existing_dollar_prices_dict()
    if today_price_date in existing_dollar_prices_dict:
        last_dollar_price: DomesticDollarPrice = existing_dollar_prices_dict.get(
            today_price_date
        )
        last_dollar_price.azad = azad_usd_price
        last_dollar_price.nima = nima_usd_price
        last_dollar_price.save()

    else:
        today_price_date_shamsi = str(
            jdatetime.date.fromgregorian(date=today_price_date)
        )

        today_price = DomesticDollarPrice.objects.create(
            date=today_price_date,
            date_shamsi=today_price_date_shamsi,
            azad=azad_usd_price,
            nima=nima_usd_price,
        )

        return today_price


def get_dollar_daily_price():

    run_main_task(
        main_task=get_dollar_daily_price_main,
    )
