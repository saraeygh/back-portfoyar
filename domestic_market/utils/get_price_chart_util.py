from django.db.models import Avg
from django.shortcuts import get_object_or_404
from domestic_market.models import DomesticCommodity, DomesticIndustry, DomesticTrade


def get_price_chart(
    industry_id,
    commodity_type_id,
    commodity_id,
    producer_id,
    commodity_name_trade_id,
) -> list | None:
    if industry_id and isinstance(industry_id, int):
        industry = get_object_or_404(DomesticIndustry, id=industry_id)
    else:
        return None

    if commodity_type_id and isinstance(commodity_type_id, int):
        commodity_types = list(industry.commodity_types.filter(id=commodity_type_id))
        commodities_list = list(
            DomesticCommodity.objects.filter(commodity_type__in=commodity_types)
        )
    else:
        return None

    if commodity_id and isinstance(commodity_id, int):
        trades = (
            DomesticTrade.objects.filter(commodity_id=commodity_id)
            .exclude(supply_volume=0)
            .exclude(competition__lt=0)
            .order_by("trade_date")
        )
    else:
        trades = (
            DomesticTrade.objects.filter(commodity__in=commodities_list)
            .exclude(supply_volume=0)
            .exclude(competition__lt=0)
            .order_by("trade_date")
        )

    if producer_id and isinstance(producer_id, int):
        trades = (
            trades.filter(producer_id=producer_id)
            .exclude(supply_volume=0)
            .order_by("trade_date")
        )

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
