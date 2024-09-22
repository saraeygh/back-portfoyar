from django.db.models import Avg
from django.shortcuts import get_object_or_404
from global_market.models import GlobalCommodity, GlobalIndustry, GlobalTrade


def get_price_chart(
    industry_id,
    commodity_type_id,
    commodity_id,
    transit_id,
) -> list | None:
    if industry_id and isinstance(industry_id, int):
        industry = get_object_or_404(GlobalIndustry, id=industry_id)
    else:
        return None

    if commodity_type_id and isinstance(commodity_type_id, int):
        commodity_types = list(industry.commodity_types.filter(id=commodity_type_id))
        commodities_list = list(
            GlobalCommodity.objects.filter(commodity_type__in=commodity_types)
        )
    else:
        return None

    if commodity_id and isinstance(commodity_id, int):
        trades = GlobalTrade.objects.filter(commodity_id=commodity_id).order_by(
            "trade_date"
        )
    else:
        trades = GlobalTrade.objects.filter(commodity__in=commodities_list).order_by(
            "trade_date"
        )

    if transit_id and isinstance(transit_id, int):
        trades = trades.filter(transit_id=transit_id).order_by("trade_date")

    trades_avg_prices = list(
        trades.values("trade_date")
        .annotate(avg_price=Avg("price"))
        .order_by("trade_date")
    )

    return trades_avg_prices
