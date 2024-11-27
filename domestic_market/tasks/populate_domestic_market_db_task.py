from core.utils import print_task_info
from domestic_market.utils import (
    populate_domestic_market_category,
    populate_domestic_market_producer,
    populate_domestic_market_trade,
)


def populate_domestic_market_db():
    print_task_info(name=__name__)

    populate_domestic_market_category()
    populate_domestic_market_producer()
    populate_domestic_market_trade()

    print_task_info(color="GREEN", name=__name__)
