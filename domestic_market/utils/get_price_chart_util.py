import pandas as pd
from datetime import datetime as dt

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from core.configs import HEZAR_RIAL_TO_MILLION_TOMAN

from domestic_market.models import (
    DomesticCommodity,
    DomesticIndustry,
    DomesticTrade,
    DomesticDollarPrice,
)


def get_commodity_trades(trades, commodity_id, commodities_list):
    if commodity_id is None:
        trades = trades.filter(commodity__in=commodities_list)
    else:
        trades = trades.filter(commodity_id=commodity_id)

    return trades


def get_producer_trades(trades, producer_id):
    if producer_id is None:
        return trades

    trades = trades.filter(producer_id=producer_id)
    return trades


def get_commodity_name_trades(trades, commodity_name_trade_id):
    if commodity_name_trade_id is None:
        return trades

    commodity_name = get_object_or_404(DomesticTrade, id=commodity_name_trade_id)
    commodity_name = commodity_name.commodity_name
    trades = trades.filter(commodity_name=commodity_name)

    return trades


def get_forward_trades(
    commodity_id, commodities_list, producer_id, commodity_name_trade_id
):
    today = dt.today().date()
    trades = (
        DomesticTrade.objects.filter(contract_type__contains="سلف")
        .exclude(delivery_date__gt=today)
        .exclude(supply_volume=0)
        .exclude(competition__lt=0)
    )

    trades = get_commodity_trades(trades, commodity_id, commodities_list)
    trades = get_producer_trades(trades, producer_id)
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


def get_non_forward_trades(
    commodity_id, commodities_list, producer_id, commodity_name_trade_id
):
    trades = (
        DomesticTrade.objects.exclude(contract_type__contains="سلف")
        .exclude(supply_volume=0)
        .exclude(competition__lt=0)
    )

    trades = get_commodity_trades(trades, commodity_id, commodities_list)
    trades = get_producer_trades(trades, producer_id)
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


def get_price_chart(
    industry_id, commodity_type_id, commodity_id, producer_id, commodity_name_trade_id
):
    industry = get_object_or_404(DomesticIndustry, id=industry_id)
    commodity_types = list(industry.commodity_types.filter(id=commodity_type_id))
    commodities_list = list(
        DomesticCommodity.objects.filter(commodity_type__in=commodity_types)
    )

    forward = get_forward_trades(
        commodity_id, commodities_list, producer_id, commodity_name_trade_id
    )

    non_forward = get_non_forward_trades(
        commodity_id, commodities_list, producer_id, commodity_name_trade_id
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
