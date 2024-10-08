import json
from celery import shared_task
from core.utils import RedisInterface, task_timing
from future_market.models import (
    BaseEquity,
    FUND_INFO,
    COMMODITY_INFO,
    GOLD_INFO,
    ID,
    CONTRACT_CODE,
)

redis_conn = RedisInterface(db=4)

BASE_EQUITY_SYMBOLS = {
    "زعفران": "SAF",
    "لوتوس": "ETC",
    "شمش": "GB",
    "كهربا": "KB",
}

NAME_COL = "name"
UNIQUE_IDENTIFIER_COL = "unique_identifier"

BASE_EQUITY_KEYS = {
    FUND_INFO: {NAME_COL: "Name", UNIQUE_IDENTIFIER_COL: ID},
    COMMODITY_INFO: {NAME_COL: "Name", UNIQUE_IDENTIFIER_COL: ID},
    GOLD_INFO: {NAME_COL: "ContractDescription", UNIQUE_IDENTIFIER_COL: CONTRACT_CODE},
}


@task_timing
@shared_task(name="update_base_equity_task")
def update_base_equity():
    print("Updating base equity list for future market ...")
    for name, symbol in BASE_EQUITY_SYMBOLS.items():
        for base_equity_key, properties in BASE_EQUITY_KEYS.items():
            try:
                data = redis_conn.client.get(name=base_equity_key)
                data = json.loads(data.decode("utf-8"))
                for datum in data:
                    base_equity_name = datum.get(properties.get(NAME_COL))
                    if name in base_equity_name:
                        BaseEquity.objects.get_or_create(
                            base_equity_key=base_equity_key,
                            base_equity_name=base_equity_name,
                            derivative_symbol=symbol,
                            unique_identifier=datum.get(
                                properties.get(UNIQUE_IDENTIFIER_COL)
                            ),
                        )
            except Exception as e:
                print(e)
                continue
    print("All base equity list for future market updated")

    print("Removing mistake rows ...")
    for mistake_row in MISTAKE_ROWS:
        mistake_obj = BaseEquity.objects.filter(
            base_equity_key=mistake_row.get("base_equity_key"),
            base_equity_name=mistake_row.get("base_equity_name"),
            derivative_symbol=mistake_row.get("derivative_symbol"),
            unique_identifier=mistake_row.get("unique_identifier"),
        )
        mistake_obj.delete()
    print("Mistake rows removed")


MISTAKE_ROWS = [
    {
        "base_equity_key": FUND_INFO,
        "base_equity_name": "صندوق س. گروه زعفران سحرخيز",
        "derivative_symbol": "SAF",
        "unique_identifier": "51200575796028449",
    },
]
