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


###############################################################################
from account.models import Profile
import pandas as pd
import jdatetime as jdt
import matplotlib.pyplot as plt
from threading import Thread


def convert_to_jalali(row):
    created_at = row.get("created_at")
    created_at = jdt.datetime.fromgregorian(datetime=created_at)
    created_at = created_at.date().strftime("%Y/%m/%d")

    return created_at


class NewUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        FILENAME = "new_users.jpg"
        users = pd.DataFrame(
            Profile.objects.values("user__username", "created_at", "note")
        )
        new_users = users["created_at"].dt.date.value_counts().reset_index()
        new_users["created_at"] = new_users.apply(convert_to_jalali, axis=1)

        plt.figure(figsize=(8, 5))
        plt.bar(
            new_users["created_at"].astype(str), new_users["count"], color="skyblue"
        )

        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.title("Occurrences per Date")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        plt.savefig(FILENAME, format="jpg", dpi=300, bbox_inches="tight")
        plt.close()

        email_thread = Thread(
            target=send_email_with_attachment, args=(FILENAME, "آمار کاربران")
        )
        email_thread.start()

        return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from samaneh.settings import BASE_DIR
from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)


def send_email_with_attachment(filename: str, task_name: str):
    email_host = EMAIL_HOST
    email_port = EMAIL_PORT
    email_host_user = EMAIL_HOST_USER
    email_host_password = EMAIL_HOST_PASSWORD
    email_to = EMAIL_TO

    subject = f"ایمیل {task_name}"

    html_body = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>

            <p style='direction: rtl; unicode-bidi: embed;'>
            آمار ثبت‌نام کاربران
            </p>

        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = email_host_user
    message["To"] = email_to
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    filepath = f"{BASE_DIR}/{filename}"

    with open(filepath, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)

    text = message.as_string()

    try:
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, email_to, text)
    except Exception as e:
        print(f"Error sending email: {e}")

    try:
        os.remove(filepath)
    except Exception:
        print(f"Error removing file: {e}")


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
