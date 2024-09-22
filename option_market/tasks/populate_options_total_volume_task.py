import jdatetime
from celery import shared_task
from tqdm import tqdm

from core.configs import OPTION_DB
from core.utils import MongodbInterface, task_timing


@task_timing
@shared_task(name="populate_option_total_volume_task")
def populate_option_total_volume():
    mongodb_conn = MongodbInterface(db_name=OPTION_DB, collection_name="history")
    option_symbols = list(
        mongodb_conn.collection.find({}, {"_id": 0, "option_symbol": 1})
    )
    option_symbols = set(option["option_symbol"] for option in option_symbols)

    today_date = jdatetime.date.today()

    total_volume_list_of_dict = []
    for day in tqdm(range(1, 366), desc="One year Total Volume", ncols=10):
        volume_date = str(today_date - jdatetime.timedelta(days=day))

        date_total_volumes_list = []
        for symbol in option_symbols:
            query_filter = {"option_symbol": symbol}
            symbol_history = mongodb_conn.collection.find_one(query_filter, {"_id": 0})
            symbol_history = symbol_history["history"]

            symbol_history = [
                history for history in symbol_history if history["date"] == volume_date
            ]

            if symbol_history:
                date_total_volumes_list.append(symbol_history[0]["volume"])

        if date_total_volumes_list:
            total_volume_list_of_dict.append(
                {
                    "date": volume_date,
                    "total_volume": sum(date_total_volumes_list),
                }
            )

    mongodb_conn = MongodbInterface(
        db_name=OPTION_DB, collection_name="one_year_total_volumes"
    )
    mongodb_conn.insert_docs_into_collection(total_volume_list_of_dict)
