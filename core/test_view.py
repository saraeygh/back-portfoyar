from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.utils import clear_redis_cache, replace_all_arabic_letters_in_db
from core.configs import MANUAL_MODE
from core.tasks import (
    is_market_open_today,
    enable_tasks_for_specific_time,
    disable_tasks_for_specific_time,
)

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

from option_market.tasks import (
    update_option_data_from_tse,
    get_option_history,
    calculate_daily_option_value,
)

from stock_market.tasks import (
    update_market_watch,
    get_monthly_activity_report_letter,
    update_stock_full_raw_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_option_value_history,
    stock_option_value_change,
    stock_option_price_spread,
    update_stock_daily_history,
    update_market_watch_indices,
)
from stock_market.utils import update_stock_adjusted_history


from dashboard.tasks import (
    dashboard_buy_sell_orders_value,
    dashboard_last_close_price,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
    dashboard_change_percent_ranges_count,
    dashboard_market_money_flow,
)

TASKS = {
    # DOMESTIC
    "11": (populate_domestic_market_db, False),
    "12": (calculate_commodity_mean_domestic, False),
    "13": (get_dollar_daily_price, False),
    "14": (calculate_monthly_sell_domestic, False),
    "15": (calculate_production_sell_domestic, False),
    "16": (get_dollar_price_history, False),
    "17": (calculate_producers_yearly_value, False),
    # GLOBAL
    "21": (calculate_commodity_means_global, False),
    # OPTION
    "31": (update_option_data_from_tse, True),
    "32": (get_option_history, False),
    "33": (calculate_daily_option_value, False),
    # STOCK
    "41": (get_monthly_activity_report_letter, False),
    "42": (update_market_watch, True),
    "43": (update_stock_full_raw_history, False),
    "44": (update_instrument_info, False),
    "45": (update_instrument_roi, True),
    "46": (stock_value_history, False),
    "47": (stock_option_value_history, False),
    "48": (stock_option_value_change, True),
    "49": (stock_option_price_spread, True),
    "491": (update_stock_adjusted_history, False),
    "492": (update_stock_daily_history, False),
    "493": (update_market_watch_indices, True),
    # FUTURE
    "51": (update_derivative_info, False),
    "52": (update_future_base_equity, False),
    "53": (update_option_base_equity, False),
    "54": (update_future, False),
    "55": (update_option_result, False),
    "56": (check_future_active_contracts, False),
    "57": (check_option_active_contracts, False),
    # DASHBOARD
    "61": (dashboard_buy_sell_orders_value, True),
    "62": (dashboard_last_close_price, True),
    "63": (dashboard_total_index, True),
    "64": (dashboard_unweighted_index, True),
    "65": (dashboard_option_value_analysis, True),
    "66": (dashboard_change_percent_ranges_count, True),
    "67": (dashboard_market_money_flow, True),
    # FUND
    "71": (get_all_fund_detail, False),
    "72": (update_fund_info, False),
    # ACCOUNT
    "91": (disable_expired_subscription, False),
    "92": (create_sub_for_all_no_sub_users, False),
    "93": (add_days_to_subs, False),
    # OTHER
    "101": (clear_redis_cache, False),
    "102": (replace_all_arabic_letters_in_db, False),
    "103": (is_market_open_today, False),
    "104": (enable_tasks_for_specific_time, False),
    "105": (disable_tasks_for_specific_time, False),
}


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        task_info = TASKS.get(request.data.get("id"))

        task = task_info[0]
        manual = task_info[1]

        if manual:
            task(MANUAL_MODE)
        else:
            task()

        return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)
