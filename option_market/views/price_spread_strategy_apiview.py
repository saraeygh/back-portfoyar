import pandas as pd
from core.configs import FIVE_MINUTES_CACHE, TO_MILLION
from core.utils import set_json_cache, get_cache_as_json, add_index_as_id
from option_market.serializers import PriceSpreadStrategySerializer
from option_market.utils import (
    CALL_OLD_NEW_COLUMN_MAPPING,
    PUT_OLD_NEW_COLUMN_MAPPING,
    convert_int_date_to_str_date,
    get_options,
)
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def calculate_strike_deviation(row):
    strike = row["strike"]
    asset_price = row["base_equit_price"]

    try:
        strike_deviation = ((strike - asset_price) / asset_price) * 100
    except ZeroDivisionError:
        strike_deviation = 0

    return strike_deviation


def get_premium(row):
    option_type = row["option_type"]
    if option_type == "call":
        return row["best_sell_price"]
    else:
        return row["best_buy_price"]


def get_strike_premium(row):
    return row["strike"] + row["premium"]


def calculate_price_spread(row):
    strike_premium = row["strike_premium"]
    asset_price = row["base_equit_price"]

    try:
        price_spread = ((strike_premium - asset_price) / asset_price) * 100
    except ZeroDivisionError:
        price_spread = 0

    return price_spread


def calculate_monthly_price_spread(row):
    days_to_expire = row["days_to_expire"]
    price_spread = row["price_spread"]

    try:
        monthly_price_spread = (price_spread / days_to_expire) * 30
    except ZeroDivisionError:
        monthly_price_spread = 0

    return monthly_price_spread


def add_stock_link(row):
    stock_link = str(row.get("base_equity_ins_code"))
    stock_link = f"https://main.tsetmc.com/InstInfo/{stock_link}/"

    return stock_link


def add_option_link(row):
    option_link = str(row.get("inst_id"))
    option_link = f"https://main.tsetmc.com/InstInfo/{option_link}/"

    return option_link


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PriceSpreadStrategyAPIView(APIView):
    def post(self, request):
        strike_deviation = int(request.data.get("strike_deviation"))
        cache_key = f"OPTIONS_PRICE_SPREAD_s_{strike_deviation}"
        cache_response = get_cache_as_json(cache_key)
        cache_response = None

        if cache_response is None:
            options_df = get_options(option_types=["option_data"])
            call_options = options_df[list(CALL_OLD_NEW_COLUMN_MAPPING.keys())]
            call_options = call_options.rename(columns=CALL_OLD_NEW_COLUMN_MAPPING)
            call_options["option_type"] = "call"

            put_options = options_df[list(PUT_OLD_NEW_COLUMN_MAPPING.keys())]
            put_options = put_options.rename(columns=PUT_OLD_NEW_COLUMN_MAPPING)
            put_options["option_type"] = "put"

            options_df = pd.concat([call_options, put_options])

            options_df["strike_deviation"] = options_df.apply(
                calculate_strike_deviation, axis=1
            )
            options_df = options_df[
                abs(options_df["strike_deviation"]) <= strike_deviation
            ]
            if options_df.empty:
                return Response(
                    {"message": "با توجه به ورودی ارائه شده نتیجه‌ای یافت نشد"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            options_df["premium"] = options_df.apply(get_premium, axis=1)

            options_df["strike_premium"] = options_df.apply(get_strike_premium, axis=1)

            options_df["price_spread"] = options_df.apply(
                calculate_price_spread, axis=1
            )

            options_df["monthly_price_spread"] = options_df.apply(
                calculate_monthly_price_spread, axis=1
            )

            options_df = options_df.sort_values(by="price_spread", ascending=False)

            options_df.reset_index(drop=True, inplace=True)
            options_df["id"] = options_df.apply(add_index_as_id, axis=1)
            options_df["expiration_date"] = options_df.apply(
                convert_int_date_to_str_date, args=("expiration_date",), axis=1
            )
            options_df["value"] = options_df["value"] / TO_MILLION
            options_df["option_link"] = options_df.apply(add_option_link, axis=1)
            options_df["stock_link"] = options_df.apply(add_stock_link, axis=1)
            options_df = options_df.to_dict(orient="records")
            options_df = PriceSpreadStrategySerializer(options_df, many=True)

            set_json_cache(cache_key, options_df.data, FIVE_MINUTES_CACHE)
            return Response(options_df.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
