from celery import shared_task
from core.utils import task_timing
from domestic_market.utils import (
    populate_domestic_market_category,
    populate_domestic_market_producer,
    populate_domestic_market_trade,
)


@task_timing
@shared_task(name="populate_domestic_market_db_task")
def populate_domestic_market_db():
    populate_domestic_market_category()

    populate_domestic_market_producer()

    populate_domestic_market_trade()
