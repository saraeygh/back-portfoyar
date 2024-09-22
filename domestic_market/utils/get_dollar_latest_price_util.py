from core.utils import get_http_response
from bs4 import BeautifulSoup
from core.configs import FA_TO_EN_TRANSLATION_TABLE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


def get_latest_dollar(URL: str):
    last_price_value = ""
    last_price_time = ""
    try:
        response = get_http_response(req_url=URL, req_headers=HEADERS)
        response = response.text
        soup = BeautifulSoup(response, "html.parser")
        soup = soup.find_all("td")

        for index, td in enumerate(soup):
            if td.string == "نرخ فعلی":
                last_price_value = soup[index + 1]
                last_price_value = int((last_price_value.string).replace(",", ""))

            if td.string == "زمان ثبت آخرین نرخ":
                last_price_time = soup[index + 1]
                last_price_time = last_price_time.string
                last_price_time = last_price_time.translate(FA_TO_EN_TRANSLATION_TABLE)

    except Exception:
        pass

    return last_price_value, last_price_time


def get_dollar_last_price():

    AZAD_URL = "https://www.tgju.org/profile/afghan_usd"
    NIMA_URL = "https://www.tgju.org/profile/nima_sell_usd"

    azad_last_price, azad_last_price_time = get_latest_dollar(URL=AZAD_URL)
    nima_last_price, nima_last_price_time = get_latest_dollar(URL=NIMA_URL)

    response = {
        "azad": {
            "price": azad_last_price,
            "time": azad_last_price_time,
            "link": AZAD_URL,
        },
        "nima": {
            "price": nima_last_price,
            "time": nima_last_price_time,
            "link": NIMA_URL,
        },
    }

    return response
