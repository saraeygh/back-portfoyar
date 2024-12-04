from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.configs import MANUAL_MODE
from core.utils import get_http_response
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
    update_market_watch_indices,
    stock_value_history,
    stock_option_price_spread,
    update_market_watch,
    stock_option_value_history,
)
from stock_market.utils import (
    stock_recommendation,
    get_recommendation_config,
    update_stock_adjusted_history,
)

from option_market.tasks import update_option_data_from_tse
from option_market.utils import populate_all_option_strategy


from future_market.tasks import (
    update_derivative_info,
    update_base_equity,
    update_future,
    update_option_result,
)
from future_market.utils import get_options_base_equity_info


class TestView(APIView):
    def get(self, request, *args, **kwargs):

        # stock_value_history()
        # stock_market_watch()
        # update_option_data_from_tse(run_mode=MANUAL_MODE)
        # update_option_result()
        # update_future_info()
        # update_base_equity()
        # update_future()
        # get_options_base_equity_info()
        # populate_option_strategy()
        # calculate_producers_yearly_value()
        # calculate_commodity_means_global()

        #######################################################################
        #######################################################################
        #######################################################################
        #######################################################################
        # add last_mean to value mean history
        # reverse the order of history
        # Round the history y values
        #######################################################################
        stock_option_value_history()
        stock_option_value_change()
        stock_option_price_spread()
        #######################################################################
        # WARINING
        # /code/stock_market/tasks/stock_option_value_history_task.py:83: UserWarning: Boolean Series key will be reindexed to match DataFrame index.
        # trade_date_options: pd.DataFrame = base_equity_options[
        #######################################################################
        #######################################################################
        #######################################################################
        #######################################################################

        # update_stock_adjusted_history()
        # update_stock_raw_adjusted_history()
        # update_instrument_info()
        # update_instrument_roi()
        # populate_all_option_strategy()
        # calculate_commodity_mean_domestic()
        # config = get_recommendation_config(user=request.user)
        # stock_recommendation(config=config)
        # res = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="long_call"))
        # update_market_watch()
        # user_generator()

        return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


# COMMON
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastDay/{ins_code} # Index Day history
# https://cdn.tsetmc.com/api/Index/GetIndexB2History/{ins_code} # Index whole history
# https://cdn.tsetmc.com/api/ClosingPrice/GetIndexCompany/{ins_code} # Index sub-companies

# Bourse
# https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/1 # Overview
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/1 # List indices
# https://cdn.tsetmc.com/api/ClosingPrice/GetTradeTop/MostVisited/1/7 # MostVisited
# https://cdn.tsetmc.com/api/Index/GetInstEffect/0/1/7 # Effects
# FaraBourse
# https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/2 # Overview
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/2 # List of indices
# https://cdn.tsetmc.com/api/ClosingPrice/GetTradeTop/MostVisited/2/7 # MostVisited
# https://cdn.tsetmc.com/api/Index/GetInstEffect/0/2/7 # Effects
