import pandas as pd

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from global_market.models import GlobalCommodity, GlobalIndustry, GlobalTrade


def get_price_chart(
    industry_id,
    commodity_type_id,
    commodity_id,
    transit_id,
) -> list | None:
    if (
        isinstance(industry_id, int)
        and industry_id != 0
        and isinstance(commodity_type_id, int)
        and commodity_type_id != 0
    ):
        industry = get_object_or_404(GlobalIndustry, id=industry_id)

        commodity_types = list(industry.commodity_types.filter(id=commodity_type_id))
        commodities_list = list(
            GlobalCommodity.objects.filter(commodity_type__in=commodity_types)
        )
    else:
        return None

    trades = GlobalTrade.objects.filter(commodity__in=commodities_list).order_by(
        "trade_date"
    )
    if isinstance(commodity_id, int) and commodity_id != 0:
        trades = GlobalTrade.objects.filter(commodity_id=commodity_id).order_by(
            "trade_date"
        )

    if isinstance(transit_id, int) and transit_id != 0:
        trades = trades.filter(transit_id=transit_id).order_by("trade_date")

    trades_avg_prices = list(
        trades.values("trade_date")
        .annotate(avg_price=Avg("price"))
        .order_by("trade_date")
    )

    return trades_avg_prices


DAYS_DELTA = 7


def get_ratio_chart(plt_1, plt_2):

    if not plt_1 or not plt_2:
        return []

    plt_1 = pd.DataFrame(plt_1)
    plt_2 = pd.DataFrame(plt_2)
    plt_1["avg_price"] = plt_1["avg_price"].astype(float)
    plt_2["avg_price"] = plt_2["avg_price"].astype(float)

    plt_1 = plt_1.sort_values("trade_date")
    plt_2 = plt_2.sort_values("trade_date")

    plt_1_start_date = plt_1.iloc[0]["trade_date"]
    plt_2_start_date = plt_2.iloc[0]["trade_date"]
    if abs((plt_2_start_date - plt_1_start_date).days) > DAYS_DELTA:
        max_start_date = max(plt_1_start_date, plt_2_start_date)
        plt_1 = plt_1[plt_1["trade_date"] >= max_start_date]
        plt_2 = plt_2[plt_2["trade_date"] >= max_start_date]
        if plt_1.empty or plt_2.empty:
            return []

        plt_1_start_date = plt_1.iloc[0]["trade_date"]
        plt_2_start_date = plt_2.iloc[0]["trade_date"]

    if plt_1_start_date == plt_2_start_date:
        pass
    elif plt_1_start_date > plt_2_start_date:
        row_at_start = {
            "trade_date": plt_2_start_date,
            "avg_price": plt_1.iloc[0].get("avg_price"),
        }

        df_start = pd.DataFrame([row_at_start])
        plt_1 = pd.concat([df_start, plt_1], ignore_index=True)
    else:
        row_at_start = {
            "trade_date": plt_1_start_date,
            "avg_price": plt_2.iloc[0].get("avg_price"),
        }

        df_start = pd.DataFrame([row_at_start])
        plt_2 = pd.concat([df_start, plt_2], ignore_index=True)

    plt_1_end_date = plt_1.iloc[-1].get("trade_date")
    plt_2_end_date = plt_2.iloc[-1].get("trade_date")
    if abs((plt_2_end_date - plt_1_end_date).days) > DAYS_DELTA:
        min_end_date = min(plt_1_end_date, plt_2_end_date)
        plt_1 = plt_1[plt_1["trade_date"] <= min_end_date]
        plt_2 = plt_2[plt_2["trade_date"] <= min_end_date]
        if plt_1.empty or plt_2.empty:
            return []

        plt_1_end_date = plt_1.iloc[-1].get("trade_date")
        plt_2_end_date = plt_2.iloc[-1].get("trade_date")

    if plt_1_end_date == plt_2_end_date:
        pass
    elif plt_1_end_date > plt_2_end_date:
        row_at_end = {
            "trade_date": plt_1_end_date,
            "avg_price": plt_2.iloc[-1].get("avg_price"),
        }

        df_end = pd.DataFrame([row_at_end])
        plt_2 = pd.concat([df_end, plt_2], ignore_index=True)
    else:
        row_at_end = {
            "trade_date": plt_2_end_date,
            "avg_price": plt_1.iloc[-1].get("avg_price"),
        }

        df_end = pd.DataFrame([row_at_end])
        plt_1 = pd.concat([df_end, plt_1], ignore_index=True)

    ratio_df = pd.merge(
        plt_1, plt_2, on="trade_date", how="outer", suffixes=("_1", "_2")
    )

    ratio_df = ratio_df.sort_values("trade_date")
    ratio_df["avg_price_1"] = ratio_df["avg_price_1"].interpolate()
    ratio_df["avg_price_2"] = ratio_df["avg_price_2"].interpolate()

    ratio_df["avg_price"] = ratio_df["avg_price_1"] / ratio_df["avg_price_2"]
    ratio_df.dropna(inplace=True)
    ratio_df = ratio_df.to_dict(orient="records")

    return ratio_df
