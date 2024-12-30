import pandas as pd

from django.shortcuts import get_object_or_404
from django.db.models import Avg

from domestic_market.models import DomesticTrade


def get_price_chart_by_producer(
    producer_id, commodity_id, commodity_name_trade_id
) -> list | None:
    if (
        producer_id
        and commodity_id
        and isinstance(producer_id, int)
        and isinstance(commodity_id, int)
    ):
        trades = (
            DomesticTrade.objects.filter(producer_id=producer_id)
            .filter(commodity_id=commodity_id)
            .exclude(supply_volume=0)
            .exclude(competition__lt=0)
            .order_by("trade_date")
        )
    else:
        return None

    if commodity_name_trade_id and isinstance(commodity_name_trade_id, int):
        commodity_name = get_object_or_404(DomesticTrade, id=commodity_name_trade_id)
        commodity_name = commodity_name.commodity_name
        trades = trades.filter(commodity_name=commodity_name)

    trades_avg_prices = list(
        trades.values("trade_date", "competition")
        .annotate(avg_price=Avg("close_price"))
        .order_by("trade_date")
    )

    unique_dates = {}
    for trade in trades_avg_prices:
        if trade["trade_date"] in unique_dates:
            last_trade = unique_dates.get(trade["trade_date"])
            new_avg_price = (last_trade["avg_price"] + trade["avg_price"]) / 2
            new_competition = (last_trade["competition"] + trade["competition"]) / 2
            unique_dates[trade["trade_date"]] = {
                "trade_date": trade["trade_date"],
                "avg_price": new_avg_price,
                "competition": new_competition,
            }
        else:
            unique_dates[trade["trade_date"]] = trade

    trades_avg_prices = list(unique_dates.values())

    return trades_avg_prices


DAYS_DELTA = 7


def get_ratio_chart(plt_1, plt_2):

    if not plt_1 or not plt_2:
        return []

    plt_1 = pd.DataFrame(plt_1)
    plt_2 = pd.DataFrame(plt_2)
    plt_1.drop("competition", axis=1, inplace=True)
    plt_2.drop("competition", axis=1, inplace=True)
    plt_1 = plt_1.sort_values("trade_date")
    plt_2 = plt_2.sort_values("trade_date")
    plt_1["avg_price"] = plt_1["avg_price"].astype(float)
    plt_2["avg_price"] = plt_2["avg_price"].astype(float)

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
    ratio_df["competition"] = 0
    ratio_df.dropna(inplace=True)
    ratio_df = ratio_df.to_dict(orient="records")

    return ratio_df
