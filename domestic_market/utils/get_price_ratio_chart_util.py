import pandas as pd
from datetime import datetime as dt

from django.shortcuts import get_object_or_404
from django.db.models import Avg

from core.configs import HEZAR_RIAL_TO_MILLION_TOMAN

from domestic_market.models import DomesticTrade, DomesticDollarPrice


def get_commodity_name_trades(trades, commodity_name_trade_id):
    if commodity_name_trade_id is None:
        return trades

    commodity_name = get_object_or_404(DomesticTrade, id=commodity_name_trade_id)
    commodity_name = commodity_name.commodity_name
    trades = trades.filter(commodity_name=commodity_name)

    return trades


def get_forward_trades(producer_id, commodity_id, commodity_name_trade_id):
    today = dt.today().date()
    trades = (
        DomesticTrade.objects.filter(producer_id=producer_id)
        .filter(commodity_id=commodity_id)
        .filter(contract_type__contains="سلف")
        .exclude(delivery_date__gt=today)
        .exclude(supply_volume=0)
        .exclude(competition__lt=0)
    )

    trades = get_commodity_name_trades(trades, commodity_name_trade_id)

    trades_avg_prices = pd.DataFrame(
        trades.values("trade_date", "competition", "delivery_date").annotate(
            avg_price=Avg("close_price")
        )
    )

    if not trades_avg_prices.empty:
        trades_avg_prices["trade_date"] = trades_avg_prices["delivery_date"]
        trades_avg_prices.drop("delivery_date", axis=1, inplace=True)

        trades_avg_prices = trades_avg_prices.groupby(
            "trade_date", as_index=False
        ).mean()

    return trades_avg_prices


def get_non_forward_trades(producer_id, commodity_id, commodity_name_trade_id):
    trades = (
        DomesticTrade.objects.filter(producer_id=producer_id)
        .filter(commodity_id=commodity_id)
        .exclude(contract_type__contains="سلف")
        .exclude(supply_volume=0)
        .exclude(competition__lt=0)
    )

    trades = get_commodity_name_trades(trades, commodity_name_trade_id)

    trades_avg_prices = pd.DataFrame(
        trades.values("trade_date", "competition").annotate(
            avg_price=Avg("close_price")
        )
    )

    if not trades_avg_prices.empty:
        trades_avg_prices = trades_avg_prices.groupby(
            "trade_date", as_index=False
        ).mean()

    return trades_avg_prices


def get_dollar_history(start, end):
    dollar_history = pd.DataFrame(
        DomesticDollarPrice.objects.filter(date__range=(start, end)).values(
            "date", "azad", "nima"
        )
    )

    return dollar_history


def get_price_chart_by_producer(producer_id, commodity_id, commodity_name_trade_id):
    forward = get_forward_trades(producer_id, commodity_id, commodity_name_trade_id)

    non_forward = get_non_forward_trades(
        producer_id, commodity_id, commodity_name_trade_id
    )

    price = pd.concat([forward, non_forward])
    if not price.empty:
        price.sort_values(by="trade_date", inplace=True, ascending=True)

        start = price.iloc[0]["trade_date"]
        end = price.iloc[-1]["trade_date"]

        dollar = get_dollar_history(start, end)
        if not dollar.empty:
            price = pd.merge(
                left=price,
                right=dollar,
                left_on="trade_date",
                right_on="date",
                how="left",
            )
            price.drop("date", axis=1, inplace=True)

            price["azad"] = price["azad"].interpolate()
            price["nima"] = price["nima"].interpolate()

            price["azad"] = price["avg_price"] * 1000 / price["azad"]
            price["nima"] = price["avg_price"] * 1000 / price["nima"]

        else:
            price["azad"] = 0
            price["nima"] = 0

        price["avg_price"] = price["avg_price"] / HEZAR_RIAL_TO_MILLION_TOMAN

    price.dropna(inplace=True)
    price = price.to_dict(orient="records")

    return price


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
