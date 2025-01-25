from datetime import datetime as dt
import pandas as pd
from tqdm import tqdm

from core.utils import get_http_response, run_main_task

from fund.models import FundType, FundInfo, UNKNOWN
from fund.utils import FIPIRAN_HEADERS, update_fund_type


def get_all_fund_reg_no_list():
    FUND_COMPARE_URL = "https://fund.fipiran.ir/api/v1/fund/fundcompare"

    funds = get_http_response(req_url=FUND_COMPARE_URL, req_headers=FIPIRAN_HEADERS)
    funds = pd.DataFrame(funds.json().get("items"))

    reg_no_list = funds["regNo"].to_list()

    return reg_no_list


def update_fund_info(fund_info_bulk_update, fund_detail):
    reg_no = fund_detail.get("regNo")

    fund_info = {
        "fund_type": FundType.objects.get(code=fund_detail.get("fundType")),
        "reg_no": reg_no,
        "name": fund_detail.get("name"),
        "invest_type": fund_detail.get("typeOfInvest") or UNKNOWN,
        "initiation_date": dt.fromisoformat(fund_detail.get("initiationDate")).date(),
        "dividend_interval_period": fund_detail.get("dividendIntervalPeriod") or 0,
        "guaranteed_earning_rate": fund_detail.get("guaranteedEarningRate") or 0,
        "last_date": dt.fromisoformat(fund_detail.get("date")).date(),
        "fund_manager": fund_detail.get("manager") or UNKNOWN,
        "market_maker": fund_detail.get("marketMaker") or UNKNOWN,
        "guarantor": fund_detail.get("guarantor") or UNKNOWN,
        "investment_manager": fund_detail.get("investmentManager") or UNKNOWN,
        "national_id": fund_detail.get("nationalId") or UNKNOWN,
        "ins_code": fund_detail.get("insCode") or UNKNOWN,
    }

    website = fund_detail.get("websiteAddress")
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

    return fund_info_bulk_update


def get_fund_detail_main():
    update_fund_type()

    reg_no_list = get_all_fund_reg_no_list()
    fund_info_bulk_update = []
    for reg_no in tqdm(reg_no_list, desc="Fund details", ncols=10):
        FUND_DETAIL_URL = "https://fund.fipiran.ir/api/v1/fund/getfund"
        FUND_DETAIL_URL = FUND_DETAIL_URL + f"?regno={reg_no}"
        fund_detail = get_http_response(
            req_url=FUND_DETAIL_URL, req_headers=FIPIRAN_HEADERS
        )
        fund_detail = fund_detail.json().get("item")

        fund_info_bulk_update = update_fund_info(fund_info_bulk_update, fund_detail)

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
                "market_maker",
                "website",
                "guarantor",
                "investment_manager",
                "national_id",
                "ins_code",
            ],
        )


def get_fund_detail():

    run_main_task(
        main_task=get_fund_detail_main,
        daily=True,
    )
