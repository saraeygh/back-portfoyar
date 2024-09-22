import pandas as pd
from core.configs import STOCK_DB, STOCK_NA_ROI
from core.utils import MongodbInterface, add_index_as_id


def get_instrument_roi(instruments):

    mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name="roi")

    instruments_roi = []
    for instrument in instruments:
        inst_roi = list(
            mongo_client.collection.find(
                {"ins_code": instrument.instrument.ins_code}, {"_id": 0}
            )
        )
        if inst_roi:
            instruments_roi = instruments_roi + inst_roi
        else:
            instruments_roi.append(
                {
                    "link": f"https://www.tsetmc.com/instInfo/{instrument}",
                    "symbol": instrument.instrument.symbol,
                    "daily_roi": 0,
                    "weekly_roi": 0,
                    "monthly_roi": 0,
                    "quarterly_roi": 0,
                    "half_yearly_roi": 0,
                    "yearly_roi": 0,
                    "three_years_roi": 0,
                    "market_cap": 0,
                    "pe": 0,
                    "sector_pe": 0,
                    "ps": 0,
                },
            )

    instruments_roi = pd.DataFrame(instruments_roi)
    if instruments_roi.empty:
        return []

    instruments_roi = instruments_roi[(instruments_roi["weekly_roi"] != STOCK_NA_ROI)]
    if instruments_roi.empty:
        return []

    instruments_roi = instruments_roi.sort_values(by="weekly_roi", ascending=False)
    instruments_roi = instruments_roi[~instruments_roi["symbol"].str.contains(r"\d")]
    if instruments_roi.empty:
        return []

    instruments_roi.reset_index(drop=True, inplace=True)
    instruments_roi["id"] = instruments_roi.apply(add_index_as_id, axis=1)
    instruments_roi = instruments_roi.to_dict(orient="records")

    return instruments_roi
