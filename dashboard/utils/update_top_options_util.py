from option_market.utils import get_option_data_from_redis

from core.utils import MongodbInterface

from core.configs import (
    DASHBOARD_MONGO_DB,
    TOP_OPTIONS_COLLECTION,
    RIAL_TO_BILLION_TOMAN,
)


def update_top_options():
    option_data = get_option_data_from_redis()
    base_equities = list(option_data["base_equity_symbol"].unique())
    top_options = []
    for base_equity_symbol in base_equities:
        new_option = {}
        base_equity_df = option_data[
            option_data["base_equity_symbol"] == base_equity_symbol
        ]

        new_option["symbol"] = base_equity_symbol
        new_option["total_value"] = int(
            (base_equity_df["call_value"].sum() + base_equity_df["put_value"].sum())
            / RIAL_TO_BILLION_TOMAN
        )

        base_equity_df = base_equity_df.sort_values(by="call_value", ascending=False)
        new_option["best_call"] = base_equity_df.iloc[0].get("call_name")
        new_option["call_value"] = (
            base_equity_df.iloc[0].get("call_value") / RIAL_TO_BILLION_TOMAN
        )

        base_equity_df = base_equity_df.sort_values(by="put_value", ascending=False)
        new_option["best_put"] = base_equity_df.iloc[0].get("put_name")
        new_option["put_value"] = (
            base_equity_df.iloc[0].get("put_value") / RIAL_TO_BILLION_TOMAN
        )

        top_options.append(new_option)

    if top_options:

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=TOP_OPTIONS_COLLECTION
        )

        mongo_conn.insert_docs_into_collection(top_options)

        mongo_conn.client.close()
