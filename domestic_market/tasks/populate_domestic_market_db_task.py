from celery_singleton import Singleton
from samaneh.celery import app

from core.utils import run_main_task

from domestic_market.utils import (
    populate_domestic_market_category,
    populate_domestic_market_producer,
    populate_domestic_market_trade,
)


def populate_domestic_market_db_main():

    populate_domestic_market_category()
    populate_domestic_market_producer()
    populate_domestic_market_trade()


@app.task(base=Singleton, name="populate_domestic_market_db_task")
def populate_domestic_market_db():

    run_main_task(
        main_task=populate_domestic_market_db_main,
        daily=True,
    )
