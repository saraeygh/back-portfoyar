from global_market.models import GlobalCommodityType


def get_commodity_type_dict() -> dict:
    all_commodity_type = GlobalCommodityType.objects.all()

    commodity_type_dict = {}
    for commodity_type in all_commodity_type:
        commodity_type_dict[(commodity_type.name, commodity_type.industry.name)] = (
            commodity_type.id
        )

    return commodity_type_dict
