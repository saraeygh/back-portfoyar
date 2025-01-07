import pandas as pd
import jdatetime

from core.utils import get_http_response

from domestic_market.models import DomesticDollarPrice, BourseViewCookie

NIMA = "nima"
AZAD = "azad"


def get_last_dollar_price(dollar: str):
    if dollar == "azad":
        last_usd_price = DomesticDollarPrice.objects.last().azad
    elif dollar == "nima":
        last_usd_price = DomesticDollarPrice.objects.last().nima

    return last_usd_price


def get_dollar_price_dict(URL: str, cat: str):

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

    response = get_http_response(req_url=URL, req_headers=HEADERS)
    prices = pd.DataFrame((response.json())["items"])
    prices["value"] = prices["value"].astype(int)
    prices["periodEndingDate"] = prices["periodEndingDate"].astype(str)

    if cat == NIMA:
        prices.rename(columns={"periodEndingDate": "date", "value": NIMA}, inplace=True)
    else:
        prices.rename(columns={"periodEndingDate": "date", "value": AZAD}, inplace=True)

    prices["date"] = pd.to_datetime(prices["date"], format="%Y%m%d")

    return prices


def get_dollar_price_history():
    NIMA_URL = "https://www.bourseview.com/api/v2/currency?fromTo=[100,106]"
    AZAD_URL = "https://www.bourseview.com/api/v2/currency?fromTo=[107,106]"

    nima_usd_price = get_dollar_price_dict(NIMA_URL, NIMA)
    azad_usd_price = get_dollar_price_dict(AZAD_URL, AZAD)

    dollars = pd.merge(left=nima_usd_price, right=azad_usd_price, on="date", how="left")
    dollars["azad"] = dollars["azad"].interpolate()
    dollars = dollars.to_dict(orient="records")

    bulk_create_list = []
    bulk_update_list = []
    for dollar in dollars:
        date = dollar.get("date")
        nima = dollar.get(NIMA)
        azad = dollar.get(AZAD)

        try:
            dollar_obj = DomesticDollarPrice.objects.get(date=date)
            dollar_obj.azad = azad
            dollar_obj.nima = nima
            bulk_update_list.append(dollar_obj)
        except DomesticDollarPrice.DoesNotExist:
            date_shamsi = str(jdatetime.date.fromgregorian(date=date))
            new_dollar = {
                "date": date,
                "date_shamsi": date_shamsi,
                "nima": nima,
                "azad": azad,
            }

            new_dollar = DomesticDollarPrice(**new_dollar)
            bulk_create_list.append(new_dollar)

    if bulk_update_list:
        DomesticDollarPrice.objects.bulk_update(bulk_update_list, fields=(NIMA, AZAD))

    if bulk_create_list:
        DomesticDollarPrice.objects.bulk_create(bulk_create_list)
