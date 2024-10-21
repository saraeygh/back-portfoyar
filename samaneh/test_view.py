from rest_framework.views import APIView
import json
import pandas as pd
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


redis_conn = RedisInterface(db=4)


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        update_option_data_from_tse()
        # update_future_info()
        # update_base_equity()
        # update_future()
        # get_options_base_equity_info()
        update_option_result()

        value = json.loads(redis_conn.client.get(name="covered_call"))

        keys = redis_conn.client.keys(pattern="*")
        result = dict()
        for key in keys:
            try:
                key = key.decode("utf-8")
                if key == "updateCDCMarketsInfo":
                    pass
                value = json.loads(redis_conn.client.get(name=key))
                dic = json.loads(redis_conn.client.get(name=key))
                value = pd.DataFrame(value)

                result[key] = value
            except Exception as e:
                continue

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
        # redis_conn = RedisInterface(db=3)
        # res = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="long_call"))

        pass


# updateAllMarketData -
# updateFutureMarketsInfo - آتی
# updateGavahiMarketsInfo -
# updateSandoqMarketsInfo - صندوق‌های کالایی
# updateCDCMarketsInfo - گواهی سپرده کالایی
