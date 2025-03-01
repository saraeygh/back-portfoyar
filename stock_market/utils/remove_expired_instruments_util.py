import pandas as pd

from django.db.models import Count
from core.utils import MongodbInterface
from core.configs import OPTION_DATA_COLLECTION, OPTION_MONGO_DB

from stock_market.models import StockInstrument
from stock_market.utils import OPTION_PAPER


def get_options():
    mongo_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
    )
    options = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

    return options


def remove_expired_options():
    active_options = get_options()
    call_options = active_options["call_ins_code"].to_list()
    put_options = active_options["put_ins_code"].to_list()
    active_options = call_options + put_options

    expired_options = StockInstrument.objects.filter(paper_type=OPTION_PAPER).exclude(
        ins_code__in=active_options
    )
    expired_options.delete()


def remove_paper_type_updated_instruments():
    repeated_symbols = (
        StockInstrument.objects.values("symbol")
        .annotate(symbol_count=Count("symbol"))
        .filter(symbol_count__gt=1)
    )

    for repeated_symbol in repeated_symbols:
        duplicate_instances = StockInstrument.objects.filter(
            symbol=repeated_symbol["symbol"]
        ).order_by("id")
        duplicate_instances.exclude(id=duplicate_instances.last().id).delete()


def remove_expired_instruments():
    remove_expired_options()
    remove_paper_type_updated_instruments()

    return StockInstrument.objects.all()
