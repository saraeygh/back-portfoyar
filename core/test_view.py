from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.utils import clear_redis_cache, replace_all_arabic_letters_in_db
from core.configs import MANUAL_MODE

from account.tasks import disable_expired_subscription
from account.utils import create_sub_for_all_no_sub_users, add_days_to_subs

from domestic_market.utils import get_dollar_price_history
from domestic_market.tasks import (
    calculate_commodity_mean_domestic,
    get_dollar_daily_price,
    populate_domestic_market_db,
    calculate_monthly_sell_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
)

from fund.tasks import update_fund_info, get_all_fund_detail

from future_market.tasks import (
    update_derivative_info,
    update_future_base_equity,
    update_option_base_equity,
    update_future,
    update_option_result,
    check_future_active_contracts,
    check_option_active_contracts,
)
from global_market.tasks import calculate_commodity_means_global

from option_market.tasks import update_option_data_from_tse, get_option_history
from option_market.utils import populate_all_option_strategy_sync

from stock_market.tasks import (
    update_market_watch,
    get_monthly_activity_report_letter,
    update_stock_raw_adjusted_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_option_value_history,
    stock_option_value_change,
    stock_option_price_spread,
)
from stock_market.utils import update_stock_adjusted_history


from dashboard.tasks import dashboard


TASKS = {
    # DOMESTIC
    "11": populate_domestic_market_db,
    "12": calculate_commodity_mean_domestic,
    "13": get_dollar_daily_price,
    "14": calculate_monthly_sell_domestic,
    "15": calculate_production_sell_domestic,
    "16": get_dollar_price_history,
    "17": calculate_producers_yearly_value,
    # GLOBAL
    "21": calculate_commodity_means_global,
    # OPTION
    "31": update_option_data_from_tse,
    "32": get_option_history,
    "33": populate_all_option_strategy_sync,
    # STOCK
    "41": get_monthly_activity_report_letter,
    "42": update_market_watch,
    "43": update_stock_raw_adjusted_history,
    "44": update_instrument_info,
    "45": update_instrument_roi,
    "46": stock_value_history,
    "47": stock_option_value_history,
    "48": stock_option_value_change,
    "49": stock_option_price_spread,
    "491": update_stock_adjusted_history,
    # FUTURE
    "51": update_derivative_info,
    "52": update_future_base_equity,
    "53": update_option_base_equity,
    "54": update_future,
    "55": update_option_result,
    "56": check_future_active_contracts,
    "57": check_option_active_contracts,
    # DASHBOARD
    "61": dashboard,
    # FUND
    "71": get_all_fund_detail,
    "72": update_fund_info,
    # ACCOUNT
    "91": disable_expired_subscription,
    "92": create_sub_for_all_no_sub_users,
    "93": add_days_to_subs,
    # OTHER
    "101": clear_redis_cache,
    "102": replace_all_arabic_letters_in_db,
}


class TestView(APIView):

    def get(self, request, *args, **kwargs):
        task_id = request.data.get("id")
        manual = request.data.get("manual")

        if manual:
            TASKS.get(task_id)(MANUAL_MODE)
        else:
            TASKS.get(task_id)()

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
# https://cdn.tsetmc.com/api/ClosingPrice/GetTradeTop/MostVisited/2/7 # MostVisitedf
# https://cdn.tsetmc.com/api/Index/GetInstEffect/0/2/7 # Effects
