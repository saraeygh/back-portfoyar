import pandas as pd

from django.db.models import Count
from core.utils import RedisInterface
from core.configs import OPTION_REDIS_DB

from stock_market.models import StockInstrument
from stock_market.utils import OPTION_PAPER


def get_options():
    redis_conn = RedisInterface(db=OPTION_REDIS_DB)
    options = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="option_data"))
    redis_conn.client.close()

    return options


def remove_expired_options():
    active_options = get_options()
    call_options = active_options["call_ins_code"].to_list()
    put_options = active_options["put_ins_code"].to_list()
    active_options = call_options + put_options

    deactive_options = StockInstrument.objects.filter(paper_type=OPTION_PAPER).exclude(
        ins_code__in=active_options
    )
    deactive_options.delete()


def remove_paper_type_updated_instruments():
    repated_symbols = (
        StockInstrument.objects.values("symbol")
        .annotate(symbol_count=Count("symbol"))
        .filter(symbol_count__gt=1)
    )

    for repeated_symbol in repated_symbols:
        duplicate_instances = StockInstrument.objects.filter(
            symbol=repeated_symbol["symbol"]
        ).order_by("id")
        duplicate_instances.exclude(id=duplicate_instances.last().id).delete()


def remove_expired_instruments():
    remove_expired_options()
    remove_paper_type_updated_instruments()

    return StockInstrument.objects.all()
