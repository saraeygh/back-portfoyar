from . import (
    populate_commodity,
    populate_commodity_type,
    populate_industry,
    populate_trade,
    populate_transit,
)


def populate_global_market_db(global_market_data: list) -> dict:
    existing_industry = populate_industry(global_market_data)

    existing_commodity_type = populate_commodity_type(
        global_market_data, existing_industry
    )

    existing_commodity = populate_commodity(global_market_data, existing_commodity_type)

    existing_transit = populate_transit(global_market_data)

    populate_trade(global_market_data, existing_commodity, existing_transit)

    return
