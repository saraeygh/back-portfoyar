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
    update_stock_full_raw_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_option_value_history,
    stock_option_value_change,
    stock_option_price_spread,
    update_stock_daily_history,
)
from stock_market.utils import update_stock_adjusted_history


from dashboard.tasks import (
    dashboard_buy_sell_orders_value,
    dashboard_last_close_price,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
)


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
    "43": update_stock_full_raw_history,
    "44": update_instrument_info,
    "45": update_instrument_roi,
    "46": stock_value_history,
    "47": stock_option_value_history,
    "48": stock_option_value_change,
    "49": stock_option_price_spread,
    "491": update_stock_adjusted_history,
    "492": update_stock_daily_history,
    # FUTURE
    "51": update_derivative_info,
    "52": update_future_base_equity,
    "53": update_option_base_equity,
    "54": update_future,
    "55": update_option_result,
    "56": check_future_active_contracts,
    "57": check_option_active_contracts,
    # DASHBOARD
    "61": dashboard_buy_sell_orders_value,
    "62": dashboard_last_close_price,
    "63": dashboard_total_index,
    "64": dashboard_unweighted_index,
    "65": dashboard_option_value_analysis,
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
# https://cdn.tsetmc.com/api/Index/GetIndexB1LastDay/32097828799138957 # Index Day history
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


# ExcelReport2025_2_19_13_30 خرید
# def create_excel(request):
#     import pandas as pd

#     turnover = request.FILES.get("turnover")
#     file_name = turnover.name

#     turnover = pd.read_excel(turnover)

#     new_excel = []
#     for _, row in turnover.iterrows():
#         row = row.to_dict()

#         desc = row.get("شرح")
#         if desc == "نقل از قبل":
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         try:
#             desc = desc.split(" ")
#         except AttributeError:
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         pure_desc = [x for x in desc if x != ""]

#         equity_name = []
#         next_index = 1
#         for item in pure_desc:
#             current_index = pure_desc.index(item)
#             if item == "تعداد":
#                 row["تعداد"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             elif item == "سهم":
#                 next_index = current_index + 1
#             elif item == "نرخ":
#                 row["قیمت"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             else:
#                 if (
#                     (current_index == next_index)
#                     and item != pure_desc[-1]
#                     and item != "به"
#                 ):
#                     equity_name.append(pure_desc[current_index])
#                     next_index = current_index + 1

#         row["دارایی"] = " ".join(equity_name)
#         new_excel.append(row)

#     new_excel = pd.DataFrame(new_excel)
#     new_excel.to_excel(f"./{file_name}")

#     return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


# pasargad-turnover-2 فروش
# def create_excel(request):
#     import pandas as pd

#     turnover = request.FILES.get("turnover")
#     file_name = turnover.name

#     turnover = pd.read_excel(turnover)

#     new_excel = []
#     for _, row in turnover.iterrows():
#         row = row.to_dict()

#         desc = row.get("شرح")
#         if desc == "نقل از قبل":
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         try:
#             desc = desc.split(" ")
#         except AttributeError:
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         pure_desc = [x for x in desc if x != ""]

#         equity_name = []
#         next_index = 1
#         for item in pure_desc:
#             current_index = pure_desc.index(item)
#             if item == "فروش":
#                 row["تعداد"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             elif item == "سهم":
#                 next_index = current_index + 1
#             elif item == "متوسط":
#                 row["قیمت"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             else:
#                 if (current_index == next_index) and item != pure_desc[-1]:
#                     equity_name.append(pure_desc[current_index])
#                     next_index = current_index + 1

#         row["دارایی"] = " ".join(equity_name)
#         new_excel.append(row)

#     new_excel = pd.DataFrame(new_excel)
#     new_excel.to_excel(f"./{file_name}")

#     return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


# pasargad-turnover-1.xlsx - خرید
# def create_excel(request):
#     import pandas as pd

#     turnover = request.FILES.get("turnover")
#     file_name = turnover.name

#     turnover = pd.read_excel(turnover)

#     new_excel = []
#     for _, row in turnover.iterrows():
#         row = row.to_dict()

#         desc = row.get("شرح")
#         if desc == "نقل از قبل":
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         try:
#             desc = desc.split(" ")
#         except AttributeError:
#             row["تعداد"] = ""
#             row["قیمت"] = ""
#             row["دارایی"] = ""
#             new_excel.append(row)
#             continue

#         pure_desc = [x for x in desc if x != ""]

#         equity_name = []
#         next_index = 1
#         for item in pure_desc:
#             current_index = pure_desc.index(item)
#             if item == "خريد":
#                 row["تعداد"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             elif item == "سهم":
#                 next_index = current_index + 1
#             elif item == "متوسط":
#                 row["قیمت"] = pure_desc[current_index + 1]
#                 next_index = current_index + 2
#             else:
#                 if (current_index == next_index) and item != pure_desc[-1]:
#                     equity_name.append(pure_desc[current_index])
#                     next_index = current_index + 1

#         row["دارایی"] = " ".join(equity_name)
#         new_excel.append(row)

#     new_excel = pd.DataFrame(new_excel)
#     new_excel.to_excel(f"./{file_name}")

#     return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)
