from global_market.models import GlobalCommodity


def get_commodity_dict() -> dict:
    all_commodity = GlobalCommodity.objects.all()

    commodity_dict = {}
    for commodity in all_commodity:
        commodity_dict[(commodity.name, commodity.commodity_type.name)] = commodity.id

    return commodity_dict
