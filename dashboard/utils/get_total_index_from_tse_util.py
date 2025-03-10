import pandas as pd

from core.utils import MongodbInterface, TSETMC_REQUEST_HEADERS, get_http_response
from core.configs import DASHBOARD_MONGO_DB, TOTAL_INDEX_DAILY_COLLECTION


TOTAL_INDEX_COLS = {
    "dEven": "date",
    "hEven": "time",
    "xDrNivJIdx004": "current_value",
    # "xPhNivJIdx004": "max_value",
    # "xPbNivJIdx004": "min_value",
    # "xVarIdxJRfV": "change_percent",
}


def convert_int_time_to_str(row):
    time = str(int(row.get("time")))
    if len(time) != 6:
        time = "0" + time
    time = f"{time[0:2]}:{time[2:4]}"

    return time


def get_total_index_from_tse():
    TOTAL_INDEX_DAY_URL = (
        "https://cdn.tsetmc.com/api/Index/GetIndexB1LastDay/32097828799138957"
    )
    total_index = get_http_response(
        req_url=TOTAL_INDEX_DAY_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    total_index = pd.DataFrame(total_index.json().get("indexB1"))
    total_index.rename(columns=TOTAL_INDEX_COLS, inplace=True)
    total_index = total_index[list(TOTAL_INDEX_COLS.values())]
    total_index = total_index[
        (total_index["time"] >= 90000) & (total_index["time"] <= 123500)
    ]
    total_index["time"] = total_index.apply(convert_int_time_to_str, axis=1)

    total_index = total_index.to_dict(orient="records")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=TOTAL_INDEX_DAILY_COLLECTION
    )

    mongo_conn.insert_docs_into_collection(total_index)
