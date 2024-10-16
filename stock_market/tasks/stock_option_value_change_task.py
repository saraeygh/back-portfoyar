from celery import shared_task
import pandas as pd
from core.utils import MongodbInterface, RedisInterface, task_timing, MARKET_STATE
from core.models import FeatureToggle, ACTIVE
from core.configs import STOCK_DB, RIAL_TO_BILLION_TOMAN, RIAL_TO_MILLION_TOMAN

from stock_market.utils import (
    MAIN_MARKET_TYPE_DICT,
    MARKET_WATCH_COLUMN_RENAME,
    get_last_market_watch_data,
    get_market_state,
)


def get_instrument_info():
    mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name="instrument_info")
    instrument_info = list(mongo_client.collection.find({}, {"_id": 0}))
    instrument_info = pd.DataFrame(instrument_info)

    return instrument_info


def get_last_options(option_type):

    redis_conn = RedisInterface(db=3)

    last_options = redis_conn.get_list_of_dicts(list_key=option_type)
    last_options = pd.DataFrame(last_options)
    last_options["close_mean"] = (
        last_options["value"] / last_options["volume"]
    ) * 10_000
    last_options = last_options[
        ["inst_id", "option_type", "asset_name", "value", "close_mean"]
    ]

    return last_options


def get_asset_options_value_change(options):

    assets = options["asset_name"].unique().tolist()
    options_list = list()
    for asset in assets:

        try:
            asset_options: pd.DataFrame = options[options["asset_name"] == asset]
            asset_options["month_mean_value"] = (
                asset_options["month_mean_volume"] * 1000 * asset_options["close_mean"]
            ) / RIAL_TO_MILLION_TOMAN
            asset_options = asset_options[asset_options["month_mean_value"] != 0]

            last_mean = float(asset_options["value"].mean())
            month_mean = float(asset_options["month_mean_value"].mean())
            value_change = last_mean / month_mean
        except Exception:
            last_mean = 0
            month_mean = 0
            value_change = 0

        new_value_change = {
            "symbol": asset,
            "last_mean": last_mean,
            "month_mean": month_mean,
            "value_change": value_change,
        }
        options_list.append(new_value_change)

    option_value_change = pd.DataFrame(options_list)
    option_value_change.dropna(inplace=True)

    return option_value_change


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def add_pe(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    eps = row.get("eps")
    try:
        pe = close_mean / eps
    except Exception:
        pe = 0

    return pe


def add_ps(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    psr = row.get("psr")
    try:
        ps = close_mean / psr
    except Exception:
        ps = 0

    return ps


def add_market_cap(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    total_share = row.get("total_share")
    try:
        market_cap = (close_mean * total_share) / RIAL_TO_BILLION_TOMAN
    except Exception:
        market_cap = 0

    return market_cap


def add_last_update(row):

    last_update = str(row.get("last_time"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


@task_timing
@shared_task(name="stock_option_value_change_task")
def stock_option_value_change():

    print("Checking stock options value change ...")
    check_market_state = FeatureToggle.objects.get(name=MARKET_STATE)
    for market_type in list(MAIN_MARKET_TYPE_DICT.keys()):
        if check_market_state.state == ACTIVE:
            market_state = get_market_state(market_type)
            if market_state != check_market_state.value:
                print("market is closed!")
                continue

        instrument_info = get_instrument_info()

        option_types = ["calls", "puts"]
        for option_type in option_types:
            options = get_last_options(option_type=option_type)

            if options.empty:
                return

            options = pd.merge(
                left=options,
                right=instrument_info,
                left_on="inst_id",
                right_on="ins_code",
                how="left",
            )

            options.dropna(inplace=True)
            options = get_asset_options_value_change(options=options)
            options = options[options["value_change"] != 0]

            options = pd.merge(
                left=options, right=instrument_info, on="symbol", how="left"
            )
            options = options[
                [
                    "ins_code",
                    "symbol",
                    "name",
                    "last_mean",
                    "month_mean",
                    "value_change",
                    "total_share",
                    "sector_pe",
                    "psr",
                    "eps",
                    "floating_volume",
                ]
            ]

            last_data = get_last_market_watch_data()
            last_data["daily_roi"] = (last_data["pc"] / last_data["py"]) * 100
            last_data = last_data.rename(columns=MARKET_WATCH_COLUMN_RENAME)
            last_data = last_data[
                ["ins_code", "closing_price", "daily_roi", "last_time"]
            ]
            options = pd.merge(left=options, right=last_data, on="ins_code", how="left")

            options["link"] = options.apply(add_link, axis=1)
            options["pe"] = options.apply(add_pe, axis=1)
            options["ps"] = options.apply(add_ps, axis=1)
            options["market_cap"] = options.apply(add_market_cap, axis=1)
            options.dropna(inplace=True)
            options["last_update"] = options.apply(add_last_update, axis=1)
            options = options.to_dict(orient="records")

            if options:
                if option_type == "calls":
                    collection_name = "call_value_change"
                elif option_type == "puts":
                    collection_name = "put_value_change"
                else:
                    continue

                mongo_client = MongodbInterface(
                    db_name=STOCK_DB, collection_name=collection_name
                )
                mongo_client.insert_docs_into_collection(documents=options)
