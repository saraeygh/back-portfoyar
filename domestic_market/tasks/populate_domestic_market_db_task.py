from core.utils import print_task_info, send_task_fail_success_email

from domestic_market.utils import (
    populate_domestic_market_category,
    populate_domestic_market_producer,
    populate_domestic_market_trade,
)


def populate_domestic_market_db_main():

    populate_domestic_market_category()
    populate_domestic_market_producer()
    populate_domestic_market_trade()


def populate_domestic_market_db():
    TASK_NAME = populate_domestic_market_db.__name__
    print_task_info(name=TASK_NAME)

    try:
        populate_domestic_market_db_main()
        send_task_fail_success_email(task_name=TASK_NAME)
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
