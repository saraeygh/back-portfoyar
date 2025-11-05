from celery_singleton import Singleton

from datetime import datetime as dt
from tqdm import tqdm

from samaneh.celery import app
from core.configs import FUND_MONGO_DB, FUND_ALL_DATA_COLLECTION
from core.utils import MongodbInterface, run_main_task

from fund.models import FundType, FundInfo, UNKNOWN
from fund.utils import update_fund_type


def update_fund_info_main():
    update_fund_type()

    mongo_conn = MongodbInterface(
        db_name=FUND_MONGO_DB, collection_name=FUND_ALL_DATA_COLLECTION
    )
    funds = list(mongo_conn.collection.find({}, {"_id": 0}))

    fund_info_bulk_update = []
    for fund in tqdm(funds, desc="Update fund info", ncols=10):
        reg_no = fund.get("regNo")

        fund_info = {
            "fund_type": FundType.objects.get(code=fund.get("fundType")),
            "reg_no": reg_no,
            "name": fund.get("name"),
            "invest_type": fund.get("typeOfInvest") or UNKNOWN,
            "initiation_date": dt.fromisoformat(fund.get("initiationDate")).date(),
            "dividend_interval_period": fund.get("dividendIntervalPeriod") or 0,
            "guaranteed_earning_rate": fund.get("guaranteedEarningRate") or 0,
            "last_date": dt.fromisoformat(fund.get("date")).date(),
            "fund_manager": fund.get("manager") or UNKNOWN,
            "guarantor": fund.get("guarantor") or UNKNOWN,
            "ins_code": fund.get("insCode") or UNKNOWN,
        }

        website = fund.get("website")
        if website:
            fund_info["website"] = website[0]

        try:
            fund = FundInfo.objects.get(reg_no=reg_no)

            for attr_name, attr_value in fund_info.items():
                setattr(fund, attr_name, attr_value)
                fund_info_bulk_update.append(fund)

        except FundInfo.DoesNotExist:
            fund = FundInfo(**fund_info)
            fund.save()

    if fund_info_bulk_update:
        FundInfo.objects.bulk_update(
            objs=fund_info_bulk_update,
            fields=[
                "name",
                "invest_type",
                "dividend_interval_period",
                "guaranteed_earning_rate",
                "last_date",
                "fund_manager",
                "website",
                "guarantor",
                "ins_code",
            ],
        )


@app.task(base=Singleton, name="update_fund_info_task")
def update_fund_info():

    run_main_task(
        main_task=update_fund_info_main,
        daily=True,
    )
