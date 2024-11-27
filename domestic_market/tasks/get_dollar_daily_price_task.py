from datetime import datetime
import jdatetime
from bs4 import BeautifulSoup

from core.utils import get_http_response, print_task_info
from domestic_market.models import DomesticDollarPrice
from domestic_market.utils import get_existing_dollar_prices_dict


def get_last_dollar_price(dollar: str):
    if dollar == "azad":
        last_usd_price = DomesticDollarPrice.objects.last().azad
    elif dollar == "nima":
        last_usd_price = DomesticDollarPrice.objects.last().nima

    return last_usd_price


def get_dollar_price_bs(URL: str, dollar: str) -> int:

    response = get_http_response(req_url=URL)
    try:
        response = response.text
        soup = BeautifulSoup(response, "html.parser")
        soup = soup.find_all("td")

        for index, td in enumerate(soup):
            if td.string == "نرخ فعلی":
                last_price_value = soup[index + 1]
                break

        last_price_value = int((last_price_value.string).replace(",", ""))

    except Exception:
        last_price_value = get_last_dollar_price(dollar=dollar)
        return last_price_value

    return last_price_value


def get_dollar_daily_price_main():
    AZAD_URL = "https://www.tgju.org/profile/price_dollar_soleymani"
    NIMA_URL = "https://www.tgju.org/profile/nima_sell_usd"

    azad_usd_price = get_dollar_price_bs(URL=AZAD_URL, dollar="azad")
    nima_usd_price = get_dollar_price_bs(URL=NIMA_URL, dollar="nima")

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


def get_dollar_daily_price() -> None:
    print_task_info(name=__name__)

    get_dollar_daily_price_main()

    print_task_info(color="GREEN", name=__name__)
