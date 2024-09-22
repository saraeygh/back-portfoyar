from datetime import datetime
from global_market.models import GlobalTrade

from tqdm import tqdm


def populate_trade(
    global_market_data: list, existing_commodity: dict, existing_transit
) -> dict:

    new_trade_bulk = []
    for row in tqdm(global_market_data, desc="Updating trades", ncols=10):
        commodity = row["commodity"]
        transit = row["transit"]
        trades = row["trades"]
        for trade_date, price in trades.items():
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
            exists = GlobalTrade.objects.filter(
                commodity__name=commodity,
                transit__transit_type=transit,
                trade_date=trade_date,
            ).exists()

            if not exists:
                commodity_id = existing_commodity.get(
                    (row["commodity"], row["commodity_type"])
                )
                transit_id = existing_transit.get((row["transit"], row["unit"]))

                new_trade = GlobalTrade(
                    commodity_id=commodity_id,
                    transit_id=transit_id,
                    trade_date=trade_date,
                    price=price,
                )

                new_trade_bulk.append(new_trade)

    if new_trade_bulk:
        GlobalTrade.objects.bulk_create(new_trade_bulk)

    return
