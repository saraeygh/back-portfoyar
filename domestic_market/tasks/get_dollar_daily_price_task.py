import time
from datetime import datetime
import jdatetime

from playwright.sync_api import sync_playwright

from core.utils import run_main_task
from domestic_market.models import DomesticDollarPrice


def get_last_dollar_price():
    return DomesticDollarPrice.objects.last()


def update_azad_price(last_dollar, today_price_date):
    with sync_playwright() as pr:
        browser = pr.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.tgju.org/")

        time.sleep(5)

        element = page.query_selector(
            "xpath=/html/body/main/div[1]/div[2]/div/ul/li[6]/span[1]/span"
        )

        last_price_value = element.inner_text()
        browser.close()

    last_price_value = int((last_price_value).replace(",", ""))

    try:
        last_dollar_price = DomesticDollarPrice.objects.get(date=today_price_date)
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


def update_nima_price(last_dollar, today_price_date):
    with sync_playwright() as pr:
        browser = pr.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        )
        page = context.new_page()

        page.goto(
            "https://ice.ir/market-view/%D8%A8%D8%A7%D8%B2%D8%A7%D8%B1-%D8%A7%D8%B1%D8%B2"
        )

        element = page.locator('a.market-view-currency[data-value="حواله"]')
        element.wait_for(state="visible", timeout=20000)
        element.scroll_into_view_if_needed()
        element.click()

        time.sleep(5)

        cell = page.query_selector(
            "xpath=/html/body/div/div/section/div[3]/div/div/table/tbody/tr[1]/td[2]"
        )
        last_price_value = cell.inner_text()

        browser.close()

    last_price_value = int((last_price_value).replace(",", ""))

    try:
        last_dollar_price = DomesticDollarPrice.objects.get(date=today_price_date)
        last_dollar_price.nima = last_price_value
        last_dollar_price.save()
    except DomesticDollarPrice.DoesNotExist:
        today_price_date_shamsi = str(
            jdatetime.date.fromgregorian(date=today_price_date)
        )

        DomesticDollarPrice.objects.create(
            date=today_price_date,
            date_shamsi=today_price_date_shamsi,
            azad=last_dollar.azad,
            nima=last_price_value,
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
