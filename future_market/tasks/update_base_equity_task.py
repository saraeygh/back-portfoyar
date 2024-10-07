import json
from celery import shared_task
from core.utils import RedisInterface, task_timing
from future_market.models import (
    BaseEquity,
    # Derivative,
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
)

redis_conn = RedisInterface(db=4)

COL = "col"
NAME = "name"

BASE_EQUITY_KEYS = {
    FUND_INFO: {COL: ID, NAME: "Name"},
    COMMODITY_INFO: {COL: ID, NAME: "Name"},
    GOLD_INFO: {COL: CONTRACT_CODE, NAME: "ContractDescription"},
}


@task_timing
@shared_task(name="update_base_equity_task")
def update_base_equity():
    print("Updating base equity list for future market ...")
    for base_equity_key, properties in BASE_EQUITY_KEYS.items():
        try:
            base_equity_col = properties.get(COL)
            data = redis_conn.client.get(name=base_equity_key)
            data = json.loads(data.decode("utf-8"))
            for datum in data:
                base_equity_value = datum.get(base_equity_col)
                base_equity_name = properties.get(NAME)
                base_equity_name = datum.get(base_equity_name)
                BaseEquity.objects.get_or_create(
                    base_equity_key=base_equity_key,
                    base_equity_col=base_equity_col,
                    base_equity_value=base_equity_value,
                    base_equity_name=base_equity_name,
                )
        except Exception:
            continue
    print("All base equity list for future market updated")
