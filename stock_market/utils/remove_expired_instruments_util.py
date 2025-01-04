import pandas as pd

from core.utils import RedisInterface
from core.configs import OPTION_REDIS_DB

from stock_market.models import StockInstrument
from stock_market.utils import OPTION_PAPER


def get_options():
    redis_conn = RedisInterface(db=OPTION_REDIS_DB)
    options = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="option_data"))

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


def remove_expired_instruments():
    remove_expired_options()

    return StockInstrument.objects.all()
