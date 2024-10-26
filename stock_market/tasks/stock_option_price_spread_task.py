from celery import shared_task
import pandas as pd
from core.configs import STOCK_OPTION_STRIKE_DEVIATION, STOCK_DB, OPTION_REDIS_DB
from core.utils import RedisInterface, task_timing, MongodbInterface, MARKET_STATE
from core.models import FeatureToggle, ACTIVE

from stock_market.utils import MAIN_MARKET_TYPE_DICT, get_market_state
from colorama import Fore, Style

redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def get_last_options(option_types):

    options = pd.DataFrame()
    for option_type in option_types:

        last_options = redis_conn.get_list_of_dicts(list_key=option_type)

        last_options = pd.DataFrame(last_options)
        if option_type == "calls":
            last_options["option_type"] = "اختیار خرید"
        else:
            last_options["option_type"] = "اختیار فروش"

        options = pd.concat([options, last_options])

    return options


def add_time(row):
    time = str(row.get("last_update"))

    try:
        time = time.replace(":", "")
        time = int(time)
    except Exception:
        time = 0

    return time


def strike_deviation(row):
    strike = int(row.get("strike"))
    asset_price = int(row.get("base_equit_price"))

    try:
        deviation = ((strike - asset_price) / asset_price) * 100
    except Exception:
        deviation = 0

    return deviation


def get_premium(row):
    if row["option_type"] == "call":
        return row["best_sell_price"]
    else:
        return row["best_buy_price"]


def get_strike_premium(row):
    return row["strike"] + row["premium"]


def price_spread(row):
    strike_premium = int(row.get("strike_premium"))
    asset_price = int(row.get("base_equit_price"))

    try:
        spread = ((strike_premium - asset_price) / asset_price) * 100
    except Exception:
        spread = 0

    return spread


def monthly_price_spread(row):
    days_to_expire = int(row.get("days_to_expire"))
    price_spread = int(row.get("price_spread"))

    try:
        monthly_spread = (price_spread / days_to_expire) * 30
    except Exception:
        monthly_spread = 0

    return monthly_spread


def add_stock_link(row):
    ins_code = str(row.get("ins_code"))
    stock_link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return stock_link


@task_timing
@shared_task(name="stock_option_price_spread_task")
def stock_option_price_spread():

    print(Fore.BLUE + "Checking stock price spread ..." + Style.RESET_ALL)
    check_market_state = FeatureToggle.objects.get(name=MARKET_STATE)
    for market_type in list(MAIN_MARKET_TYPE_DICT.keys()):
        if check_market_state.state == ACTIVE:
            market_state = get_market_state(market_type)
            if market_state != check_market_state.value:
                print(Fore.RED + "market is closed!" + Style.RESET_ALL)
                continue

        spreads = get_last_options(["calls", "puts"])

        if not spreads.empty:
            spreads["time"] = spreads.apply(add_time, axis=1)
            spreads = spreads[spreads["time"] > 90000]

            spreads["strike_deviation"] = spreads.apply(strike_deviation, axis=1)
            spreads = spreads[
                abs(spreads["strike_deviation"]) < STOCK_OPTION_STRIKE_DEVIATION
            ]

            if not spreads.empty:
                spreads["premium"] = spreads.apply(get_premium, axis=1)
                spreads["strike_premium"] = spreads.apply(get_strike_premium, axis=1)
                spreads["price_spread"] = spreads.apply(price_spread, axis=1)

                spreads["monthly_price_spread"] = spreads.apply(
                    monthly_price_spread, axis=1
                )

                mongo_client = MongodbInterface(
                    db_name=STOCK_DB, collection_name="instrument_info"
                )
                ins_info = pd.DataFrame(
                    list(mongo_client.collection.find({}, {"_id": 0}))
                )
                ins_info = ins_info[["symbol", "ins_code"]]
                ins_info = ins_info.rename(columns={"symbol": "sym"})

                spreads = pd.merge(
                    left=spreads,
                    right=ins_info,
                    left_on="asset_name",
                    right_on="sym",
                    how="left",
                )
                spreads.dropna(inplace=True)
                spreads = spreads.rename(columns={"link": "option_link"})
                spreads["stock_link"] = spreads.apply(add_stock_link, axis=1)

                spreads = spreads[
                    [
                        "inst_id",
                        "option_link",
                        "ins_code",
                        "stock_link",
                        "last_update",
                        "symbol",
                        "asset_name",
                        "base_equit_price",
                        "strike",
                        "monthly_price_spread",
                        "days_to_expire",
                        "price_spread",
                        "expiration_date",
                        "option_type",
                        "value",
                        "premium",
                        "strike_premium",
                    ]
                ]
        else:
            spreads = pd.DataFrame()

        spreads = spreads.to_dict(orient="records")

        if spreads:
            mongo_client = MongodbInterface(
                db_name=STOCK_DB, collection_name="option_price_spread"
            )
            mongo_client.insert_docs_into_collection(documents=spreads)

            return
