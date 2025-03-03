import pandas as pd

from core.utils import MongodbInterface
from core.configs import OPTION_MONGO_DB, OPTION_DATA_COLLECTION


def get_option_data_from_mongo():
    mongo_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
    )
    option_data = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

    return option_data
