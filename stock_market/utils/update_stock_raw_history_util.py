import pandas as pd
from stock_market.models import StockRawHistory, StockInstrument
from . import HISTORY_COLUMN_RENAME


def update_stock_raw_history(
    raw_history: pd.DataFrame,
    instrument_obj: StockInstrument,
):

    if not raw_history.empty:
        model_fields_colmuns = list(HISTORY_COLUMN_RENAME.values())
        raw_history = raw_history[model_fields_colmuns]
        prev_history = list(
            StockRawHistory.objects.filter(instrument=instrument_obj).values_list(
                "trade_date", flat=True
            )
        )

        raw_history = raw_history[~raw_history["trade_date"].isin(prev_history)]
        if not raw_history.empty:
            raw_history["instrument"] = instrument_obj

        raw_history = raw_history.to_dict(orient="records")

        raw_history_bulk_list = []
        for history in raw_history:
            new_history = StockRawHistory(**history)
            raw_history_bulk_list.append(new_history)

        if raw_history_bulk_list:
            StockRawHistory.objects.bulk_create(raw_history_bulk_list)
