from time import sleep
from datetime import datetime, date
from tqdm import tqdm
import pandas as pd
from colorama import Fore, Style

from core.configs import AUTO_MODE, MANUAL_MODE, STOCK_DAILY_HISTORY_DELAY
from core.utils import run_main_task

from stock_market.utils import (
    update_get_existing_industrial_group,
    update_get_existing_instrument,
    get_market_watch_data_from_redis,
    update_stock_adjusted_history,
    remove_expired_instruments,
    is_market_open,
)
from stock_market.models import StockInstrument, StockRawHistory


def add_today_history(today_history: pd.DataFrame):
    today_history = today_history.to_dict(orient="records")

    raw_history_bulk = []
    for history in tqdm(today_history, desc="Daily history", ncols=10):
        instrument = StockInstrument.objects.get(ins_code=history["ins_code"])
        trade_date = datetime.strptime(history["last_date"], "%Y-%m-%d").date()

        prev_history = StockRawHistory.objects.filter(
            instrument=instrument, trade_date=trade_date
        ).first()
        if prev_history is None:
            close_mean = int(history["closing_price"])
            new_history = {
                "instrument": instrument,
                "trade_date": trade_date,
                "trade_count": history["trade_count"],
                "volume": int(history["volume"]),
                "value": int(history["value"]),
                "yesterday_price": int(history["yesterday_price"]),
                "open": int(history["first_price"]),
                "close": int(history["last_price"]),
                "low": int(history["min_price"]),
                "high": int(history["max_price"]),
                "close_mean": close_mean,
                "individual_buy_count": int(history["individual_buy_count"]),
                "individual_buy_volume": int(history["individual_buy_volume"]),
                "individual_buy_value": int(
                    history["individual_buy_volume"] * close_mean
                ),
                "individual_sell_count": int(history["individual_sell_count"]),
                "individual_sell_volume": int(history["individual_sell_volume"]),
                "individual_sell_value": int(
                    history["individual_sell_volume"] * close_mean
                ),
                "legal_buy_count": int(history["legal_buy_count"]),
                "legal_buy_volume": int(history["legal_buy_volume"]),
                "legal_buy_value": int(history["legal_buy_volume"] * close_mean),
                "legal_sell_count": int(history["legal_sell_count"]),
                "legal_sell_volume": int(history["legal_sell_volume"]),
                "legal_sell_value": int(history["legal_sell_volume"] * close_mean),
            }
            new_history = StockRawHistory(**new_history)
            raw_history_bulk.append(new_history)

    if raw_history_bulk:
        StockRawHistory.objects.bulk_create(raw_history_bulk)


def update_stock_daily_history_main(run_mode: str = AUTO_MODE):
    if not is_market_open() or run_mode == MANUAL_MODE:
        print(Fore.BLUE + "update_get_existing_industrial_group" + Style.RESET_ALL)
        update_get_existing_industrial_group()

        print(Fore.BLUE + "update_get_existing_instrument" + Style.RESET_ALL)
        update_get_existing_instrument()

        print(Fore.BLUE + "remove_expired_instruments" + Style.RESET_ALL)
        remove_expired_instruments()

        today_date = date.today().strftime("%Y-%m-%d")
        today_history = get_market_watch_data_from_redis()
        if today_date != today_history.iloc[0].get("last_date", "no_date"):
            return

        add_today_history(today_history)

    else:
        sleep(STOCK_DAILY_HISTORY_DELAY)
        update_stock_daily_history()

    update_stock_adjusted_history()


def update_stock_daily_history(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_stock_daily_history_main,
        kw_args={"run_mode": run_mode},
        daily=True,
    )
