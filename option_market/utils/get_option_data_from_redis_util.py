import pandas as pd

from core.utils import RedisInterface
from core.configs import OPTION_REDIS_DB


def get_option_data_from_redis():
    redis_conn = RedisInterface(db=OPTION_REDIS_DB)
    option_data = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="option_data"))
    redis_conn.client.close()

    return option_data
