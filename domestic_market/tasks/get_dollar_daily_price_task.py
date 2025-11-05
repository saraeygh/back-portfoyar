from datetime import datetime
import jdatetime
from celery_singleton import Singleton
from playwright.sync_api import sync_playwright

from samaneh.celery import app

from core.utils import run_main_task
from domestic_market.models import DomesticDollarPrice


def get_last_dollar_price():
    last_price = DomesticDollarPrice.objects.order_by("-date").first()

    return last_price


def update_azad_price(last_dollar: DomesticDollarPrice, today_price_date):
    with sync_playwright() as pr:
        browser = pr.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.tgju.org/", wait_until="networkidle")

        page.wait_for_selector(
            "xpath=/html/body/main/div[1]/div[2]/div/ul/li[6]/span[1]/span"
        )

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

        page.goto("https://ice.ir/", wait_until="networkidle")

        page.wait_for_selector(
            "xpath=/html/body/div[2]/main/div/div[1]/div[1]/section/div[4]/div/div[1]/div[1]/div[2]/div/div/div[2]/div[2]"
        )

        table = page.query_selector(
            "xpath=/html/body/div[2]/main/div/div[1]/div[1]/section/div[4]/div/div[1]/div[1]/div[2]/div/div/div[2]/div[2]"
        )

        child_divs = table.query_selector_all("div")

        for _, child in enumerate(child_divs):
            p_elements = child.query_selector_all("p")
            p_texts = [p.inner_text() for p in p_elements]
            if "دلار آمریکا" in p_texts:
                for p_text in p_texts:
                    if "ریال" in p_text:
                        last_price_value = p_text
                break
            else:
                continue

        browser.close()

    last_price_value = int((last_price_value).replace("ریال", "").replace(",", ""))

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

    try:
        update_azad_price(last_dollar, today_price_date)
    except Exception:
        update_nima_price(last_dollar, today_price_date)


@app.task(base=Singleton, name="get_dollar_daily_price_task", expires=120)
def get_dollar_daily_price():

    run_main_task(
        main_task=get_dollar_daily_price_main,
    )
