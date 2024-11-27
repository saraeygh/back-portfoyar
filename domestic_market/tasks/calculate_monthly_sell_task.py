from django.db.models import Avg, Sum, Min, Max

import jdatetime
from tqdm import trange


from domestic_market.models import (
    DomesticTrade,
    DomesticMonthlySell,
)


def calculate_end_date(start_date: jdatetime.date):
    end_date_month = start_date.month + 1 if start_date.month < 12 else 1

    end_date_year = start_date.year + 1 if end_date_month == 1 else start_date.year

    end_date = jdatetime.date(end_date_year, end_date_month, 1) - jdatetime.timedelta(
        days=1
    )

    return end_date


def calculate_month_sell(start_date, end_date):
    bulk_monthly_list = []
    start_date_gregorian = jdatetime.date.togregorian(start_date)
    end_date_gregorian = jdatetime.date.togregorian(end_date)

    trades = DomesticTrade.objects.filter(
        trade_date__range=(start_date_gregorian, end_date_gregorian)
    )

    producers_id_list = trades.distinct("producer").values_list("producer", flat=True)

    for producer_id in producers_id_list:
        commodities_name_list = (
            trades.filter(producer_id=producer_id)
            .distinct("commodity_name")
            .values_list("commodity_name", flat=True)
        )

        for commodity_name in commodities_name_list:

            exclude_in_advance_trades = (
                trades.filter(producer_id=producer_id)
                .filter(commodity_name=commodity_name)
                .exclude(contract_type__contains="سلف")
            )

            excluded_monthly_sell: dict = exclude_in_advance_trades.aggregate(
                min_value=Min("value"),
                max_value=Max("value"),
                mean_value=Avg("value"),
                total_value=Sum("value"),
                monthly_min_base_price=Min("base_price"),
                monthly_max_base_price=Max("base_price"),
                monthly_mean_base_price=Avg("base_price"),
                monthly_min_price=Min("min_price"),
                monthly_max_price=Max("max_price"),
                monthly_min_close_price=Min("close_price"),
                monthly_max_close_price=Max("close_price"),
                monthly_mean_close_price=Avg("close_price"),
            )

            within_month_in_advance_trades = (
                DomesticTrade.objects.filter(producer_id=producer_id)
                .filter(commodity_name=commodity_name)
                .filter(contract_type__contains="سلف")
                .filter(delivery_date__range=(start_date_gregorian, end_date_gregorian))
            )

            within_monthly_sell: dict = within_month_in_advance_trades.aggregate(
                min_value=Min("value"),
                max_value=Max("value"),
                mean_value=Avg("value"),
                total_value=Sum("value"),
                monthly_min_base_price=Min("base_price"),
                monthly_max_base_price=Max("base_price"),
                monthly_mean_base_price=Avg("base_price"),
                monthly_min_price=Min("min_price"),
                monthly_max_price=Max("max_price"),
                monthly_min_close_price=Min("close_price"),
                monthly_max_close_price=Max("close_price"),
                monthly_mean_close_price=Avg("close_price"),
            )

            if exclude_in_advance_trades and within_month_in_advance_trades:
                monthly_sell = {
                    "min_value": min(
                        excluded_monthly_sell["min_value"],
                        within_monthly_sell["min_value"],
                    ),
                    "max_value": max(
                        excluded_monthly_sell["max_value"],
                        within_monthly_sell["max_value"],
                    ),
                    "mean_value": (
                        (
                            excluded_monthly_sell["mean_value"]
                            + within_monthly_sell["mean_value"]
                        )
                        / 2
                    ),
                    "total_value": (
                        excluded_monthly_sell["total_value"]
                        + within_monthly_sell["total_value"]
                    ),
                    "monthly_min_base_price": min(
                        excluded_monthly_sell["monthly_min_base_price"],
                        within_monthly_sell["monthly_min_base_price"],
                    ),
                    "monthly_max_base_price": max(
                        excluded_monthly_sell["monthly_max_base_price"],
                        within_monthly_sell["monthly_max_base_price"],
                    ),
                    "monthly_mean_base_price": (
                        (
                            excluded_monthly_sell["monthly_mean_base_price"]
                            + within_monthly_sell["monthly_mean_base_price"]
                        )
                        / 2
                    ),
                    "monthly_min_price": min(
                        excluded_monthly_sell["monthly_min_price"],
                        within_monthly_sell["monthly_min_price"],
                    ),
                    "monthly_max_price": max(
                        excluded_monthly_sell["monthly_max_price"],
                        within_monthly_sell["monthly_max_price"],
                    ),
                    "monthly_min_close_price": min(
                        excluded_monthly_sell["monthly_min_close_price"],
                        within_monthly_sell["monthly_min_close_price"],
                    ),
                    "monthly_max_close_price": max(
                        excluded_monthly_sell["monthly_max_close_price"],
                        within_monthly_sell["monthly_max_close_price"],
                    ),
                    "monthly_mean_close_price": (
                        (
                            excluded_monthly_sell["monthly_mean_close_price"]
                            + within_monthly_sell["monthly_mean_close_price"]
                        )
                        / 2
                    ),
                }

            elif exclude_in_advance_trades and not within_month_in_advance_trades:
                monthly_sell = excluded_monthly_sell
            elif not exclude_in_advance_trades and within_month_in_advance_trades:
                monthly_sell = within_monthly_sell
            else:
                continue

            commodity_trade = (
                trades.filter(producer_id=producer_id)
                .filter(commodity_name=commodity_name)
                .first()
            )

            monthly_sell["producer_id"] = producer_id
            monthly_sell["commodity_id"] = commodity_trade.commodity.id
            monthly_sell["commodity_name"] = commodity_name
            monthly_sell["symbol"] = commodity_trade.symbol

            monthly_sell["start_date"] = start_date_gregorian
            monthly_sell["end_date"] = end_date_gregorian

            min_price = monthly_sell["monthly_min_price"]
            max_price = monthly_sell["monthly_max_price"]
            monthly_sell["monthly_mean_price"] = (min_price + max_price) // 2

            monthly_sell["mean_value"] = int(monthly_sell["mean_value"])
            monthly_sell["monthly_mean_base_price"] = int(
                monthly_sell["monthly_mean_base_price"]
            )
            monthly_sell["monthly_mean_close_price"] = int(
                monthly_sell["monthly_mean_close_price"]
            )

            previous_monthly_sell = (
                DomesticMonthlySell.objects.filter(producer_id=producer_id)
                .filter(commodity_id=commodity_trade.commodity.id)
                .filter(commodity_name=commodity_name)
                .filter(start_date=start_date_gregorian)
                .filter(end_date=end_date_gregorian)
            )

            cnt = previous_monthly_sell.count()
            if cnt == 0:
                new_monthly_sell = DomesticMonthlySell(**monthly_sell)
                bulk_monthly_list.append(new_monthly_sell)
            elif cnt == 1:
                previous_monthly_sell = previous_monthly_sell.first()
                previous_monthly_sell.min_value = monthly_sell["min_value"]
                previous_monthly_sell.max_value = monthly_sell["max_value"]
                previous_monthly_sell.total_value = monthly_sell["total_value"]

                previous_monthly_sell.monthly_min_base_price = monthly_sell[
                    "monthly_min_base_price"
                ]
                previous_monthly_sell.monthly_max_base_price = monthly_sell[
                    "monthly_max_base_price"
                ]
                previous_monthly_sell.monthly_mean_base_price = monthly_sell[
                    "monthly_mean_base_price"
                ]

                previous_monthly_sell.monthly_min_price = monthly_sell[
                    "monthly_min_price"
                ]
                previous_monthly_sell.monthly_max_price = monthly_sell[
                    "monthly_max_price"
                ]
                previous_monthly_sell.monthly_mean_price = monthly_sell[
                    "monthly_mean_price"
                ]

                previous_monthly_sell.monthly_min_close_price = monthly_sell[
                    "monthly_min_close_price"
                ]
                previous_monthly_sell.monthly_max_close_price = monthly_sell[
                    "monthly_max_close_price"
                ]
                previous_monthly_sell.monthly_mean_close_price = monthly_sell[
                    "monthly_mean_close_price"
                ]
                previous_monthly_sell.save()
            else:
                pass

    if bulk_monthly_list:
        bulk_created_list = DomesticMonthlySell.objects.bulk_create(bulk_monthly_list)
    else:
        bulk_created_list = []

    return bulk_created_list


def calculate_monthly_sell_domestic() -> None:
    if DomesticMonthlySell.objects.exists():
        last_monthly_sell_date = DomesticMonthlySell.objects.last().start_date
        last_monthly_sell_date = jdatetime.date.fromgregorian(
            date=last_monthly_sell_date, locale="fa_IR"
        )
        start_date = jdatetime.date(
            last_monthly_sell_date.year, last_monthly_sell_date.month, 1
        )
    elif DomesticTrade.objects.exists():
        first_trade = DomesticTrade.objects.first().trade_date
        first_trade = jdatetime.date.fromgregorian(date=first_trade, locale="fa_IR")
        start_date = jdatetime.date(first_trade.year, first_trade.month, 1)
    else:
        return

    today_date = jdatetime.date.today()
    duration = today_date - start_date
    iter_num = (duration.days // 30) + 1

    for _ in trange(iter_num, desc="Calculting monthly sell", ncols=10):
        end_date = calculate_end_date(start_date=start_date)

        calculate_month_sell(start_date=start_date, end_date=end_date)

        start_date = end_date + jdatetime.timedelta(days=1)
