from django.shortcuts import get_object_or_404
from global_market.models import (
    GlobalCommodity,
    GlobalCommodityType,
    GlobalIndustry,
    GlobalTransit,
)


def global_validate_favorite(
    industry_id: int,
    commodity_type_id: int,
    commodity_id: int,
    transit_id: int,
) -> dict | None:
    favorite_chart_dict = {}

    if industry_id and isinstance(industry_id, int):
        industry = get_object_or_404(GlobalIndustry, id=industry_id)
        favorite_chart_dict["industry"] = industry.id
    else:
        return None

    if commodity_type_id and isinstance(commodity_type_id, int):
        commodity_type = get_object_or_404(GlobalCommodityType, id=commodity_type_id)
        favorite_chart_dict["commodity_type"] = commodity_type.id
    else:
        return None

    if commodity_id and isinstance(commodity_id, int):
        commodity = get_object_or_404(GlobalCommodity, id=commodity_id)
        favorite_chart_dict["commodity"] = commodity.id
    else:
        favorite_chart_dict["commodity"] = None

    if transit_id and isinstance(transit_id, int):
        transit = get_object_or_404(GlobalTransit, id=transit_id)
        favorite_chart_dict["transit"] = transit.id
    else:
        favorite_chart_dict["transit"] = None

    return favorite_chart_dict
