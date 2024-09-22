from django.shortcuts import get_object_or_404
from domestic_market.models import DomesticProducer, DomesticCommodity, DomesticTrade


def domestic_validate_favorite_by_producer(
    producer_id: int, commodity_id: int, trade_commodity_name_id: int
) -> dict | None:
    favorite_chart_dict = {}

    if producer_id and isinstance(producer_id, int):
        producer = get_object_or_404(DomesticProducer, id=producer_id)
        favorite_chart_dict["producer"] = producer.id
    else:
        return None

    if commodity_id and isinstance(commodity_id, int):
        commodity = get_object_or_404(DomesticCommodity, id=commodity_id)
        favorite_chart_dict["commodity"] = commodity.id
    else:
        return None

    if trade_commodity_name_id and isinstance(trade_commodity_name_id, int):
        trade_commodity_name = get_object_or_404(
            DomesticTrade, id=trade_commodity_name_id
        )
        favorite_chart_dict["trade_commodity_name"] = trade_commodity_name.id
    else:
        favorite_chart_dict["trade_commodity_name"] = None

    return favorite_chart_dict
