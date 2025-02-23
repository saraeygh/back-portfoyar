import pandas as pd

from core.utils import MongodbInterface, TSETMC_REQUEST_HEADERS, get_http_response
from core.configs import DASHBOARD_MONGO_DB, UNWEIGHTED_INDEX_DAILY_COLLECTION


UNWEIGHTED_INDEX_COLS = {
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


def get_unweighted_index_from_tse():
    UNWEIGHTED_INDEX_DAY_URL = (
        "https://cdn.tsetmc.com/api/Index/GetIndexB1LastDay/67130298613737946"
    )
    unweighted_index = get_http_response(
        req_url=UNWEIGHTED_INDEX_DAY_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    unweighted_index = pd.DataFrame(unweighted_index.json().get("indexB1"))
    unweighted_index.rename(columns=UNWEIGHTED_INDEX_COLS, inplace=True)
    unweighted_index = unweighted_index[list(UNWEIGHTED_INDEX_COLS.values())]
    unweighted_index["time"] = unweighted_index.apply(convert_int_time_to_str, axis=1)

    unweighted_index = unweighted_index.to_dict(orient="records")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=UNWEIGHTED_INDEX_DAILY_COLLECTION
    )

    mongo_conn.insert_docs_into_collection(unweighted_index)

    mongo_conn.client.close()
