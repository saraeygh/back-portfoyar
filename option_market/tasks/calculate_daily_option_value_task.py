from celery_singleton import Singleton
from datetime import datetime as dt, timedelta as td
import pandas as pd
from tqdm import trange


from samaneh.celery import app

from core.utils import run_main_task
from core.configs import RIAL_TO_MILLION_TOMAN, OPTION_VALUE_ANALYSIS_DURATION


from stock_market.models import StockRawHistory
from stock_market.utils import STOCK_PAPER, INITIAL_MARKET_PAPER, PRIORITY_PAPER

from option_market.models import OptionValue


def calculate_option_value(current_date):
    date_history = pd.DataFrame(
        StockRawHistory.objects.filter(trade_date=current_date).values(
            "trade_date", "value", "instrument__paper_type", "instrument__name"
        )
    )

    if date_history.empty:
        return None, False

    market_value = date_history[
        date_history["instrument__paper_type"].isin(
            [STOCK_PAPER, INITIAL_MARKET_PAPER, PRIORITY_PAPER]
        )
    ]["value"].sum()

    call_value = date_history[
        date_history["instrument__name"].str.contains("اختیارخ", na=False)
    ]["value"].sum()

    put_value = date_history[
        date_history["instrument__name"].str.contains("اختیارف", na=False)
    ]["value"].sum()

    option_value = call_value + put_value

    if call_value == 0:
        put_to_call = 0
    else:
        put_to_call = round(put_value / call_value, 4)

    if market_value == 0:
        option_to_market = 0
    else:
        option_to_market = round(option_value / market_value, 4)

    new_obj = {
        "date": current_date,
        "call_value": call_value / RIAL_TO_MILLION_TOMAN,
        "put_value": put_value / RIAL_TO_MILLION_TOMAN,
        "option_value": option_value / RIAL_TO_MILLION_TOMAN,
        "put_to_call": put_to_call,
        "option_to_market": option_to_market,
    }

    try:
        old_option_value = OptionValue.objects.get(date=current_date)
        old_option_value.call_value = new_obj["call_value"]
        old_option_value.put_value = new_obj["put_value"]
        old_option_value.option_value = new_obj["option_value"]
        old_option_value.put_to_call = new_obj["put_to_call"]
        old_option_value.option_to_market = new_obj["option_to_market"]

        return old_option_value, False

    except OptionValue.DoesNotExist:
        new_option_value = OptionValue(**new_obj)

        return new_option_value, True


def update_database(bulk_create_list, bulk_update_list):
    if bulk_create_list:
        OptionValue.objects.bulk_create(bulk_create_list)

    if bulk_update_list:
        OptionValue.objects.bulk_update(
            objs=bulk_update_list,
            fields=[
                "call_value",
                "put_value",
                "option_value",
                "put_to_call",
                "option_to_market",
            ],
        )


def calculate_daily_option_value_task_main():
    today_date = dt.today().date()
    start_date = today_date - td(days=OPTION_VALUE_ANALYSIS_DURATION)

    bulk_create_list = []
    bulk_update_list = []

    current_date = start_date
    for _ in trange(
        (OPTION_VALUE_ANALYSIS_DURATION + 1), desc="Calculating Option Value", ncols=10
    ):
        option_value_obj, created = calculate_option_value(current_date)

        if created and option_value_obj:
            bulk_create_list.append(option_value_obj)
        elif not created and option_value_obj:
            bulk_update_list.append(option_value_obj)
        else:
            pass

        current_date = current_date + td(days=1)

    update_database(bulk_create_list, bulk_update_list)


@app.task(base=Singleton, name="calculate_daily_option_value_task", expires=60)
def calculate_daily_option_value():
    run_main_task(
        main_task=calculate_daily_option_value_task_main,
        daily=True,
    )
