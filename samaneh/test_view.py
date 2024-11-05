from rest_framework.views import APIView
import json
import pandas as pd
from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface
from option_market.utils import populate_all_option_strategy
from option_market.tasks import update_option_data_from_tse

from domestic_market.tasks import (
    calculate_producers_yearly_value,
    calculate_commodity_mean_domestic,
)
from global_market.tasks import calculate_commodity_means_global
from stock_market.tasks import (
    update_instrument_roi,
    update_instrument_info,
    update_stock_raw_adjusted_history,
    stock_option_value_change,
    stock_market_watch,
    stock_value_history,
    stock_option_price_spread,
)
from stock_market.utils import (
    stock_recommendation,
    get_recommendation_config,
    update_stock_adjusted_history,
)

from option_market.utils import populate_all_option_strategy
from option_market.tasks import update_option_data_from_tse

from rest_framework.authtoken.models import Token
import requests
from datetime import datetime

import time

from future_market.tasks import (
    update_derivative_info,
    update_base_equity,
    update_future,
    update_option_result,
)

from future_market.utils import get_options_base_equity_info


redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


def generate_password():
    import string
    import random

    ASCII_LETTERS = string.ascii_letters
    ASCII_LETTERS.replace("I", "")
    ASCII_LETTERS.replace("l", "")
    DIGITS = string.digits
    PUNC = "#$@&"

    PASS_LEN = 9
    password = ""
    password += random.choice(ASCII_LETTERS)

    CHAR_LIST = [ASCII_LETTERS, DIGITS, PUNC]
    for _ in range(PASS_LEN):
        character_type = random.choice(CHAR_LIST)
        password += random.choice(character_type)

    return password


def user_generator():
    users = []
    for user_id in range(1, 152):
        user = {
            "username": "portfoyar" + f"{user_id}",
            "password": generate_password(),
            "email": "",
            "first_name": "",
            "last_name": "",
        }
        users.append(user)

    users = pd.DataFrame(users)
    users.to_excel("./users.xlsx")
    return users


from core.tasks import collect_user_stats
from scheduler.portfoyar_scheduler_util import portfoyar_scheduler


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        portfoyar_scheduler()
        # collect_user_stats()
        # stock_option_price_spread()
        # stock_value_history()
        # stock_market_watch()
        # update_option_data_from_tse()
        # update_option_result()
        # update_future_info()
        # update_base_equity()
        # update_future()
        # get_options_base_equity_info()
        # populate_option_strategy()
        # calculate_producers_yearly_value()
        # calculate_commodity_means_global()
        # stock_option_value_change()
        # update_stock_adjusted_history()
        # update_stock_raw_adjusted_history()
        # update_instrument_info()
        # update_instrument_roi()
        # update_option_data_from_tse()
        # populate_all_option_strategy()
        # calculate_commodity_mean_domestic()
        # config = get_recommendation_config(user=request.user)
        # stock_recommendation(config=config)
        # res = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="long_call"))

        # user_generator()
        pass
        print("JOB CREATED")
