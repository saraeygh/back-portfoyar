import pandas as pd
from core.utils import RedisInterface
from core.configs import OPTION_REDIS_DB


def get_options(option_types):

    redis_conn = RedisInterface(db=OPTION_REDIS_DB)
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
