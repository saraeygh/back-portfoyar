from domestic_market.utils import (
    populate_domestic_market_category,
    populate_domestic_market_producer,
    populate_domestic_market_trade,
)


def populate_domestic_market_db():
    populate_domestic_market_category()

    populate_domestic_market_producer()

    populate_domestic_market_trade()
