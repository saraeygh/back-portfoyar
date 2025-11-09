from celery import shared_task

from core.configs import FUND_MONGO_DB, FUND_ALL_DATA_COLLECTION, MANUAL_MODE, AUTO_MODE

from core.utils import MongodbInterface, get_http_response, run_main_task

from stock_market.utils import is_in_schedule

from fund.utils import FIPIRAN_HEADERS


def get_all_fund_detail_main(run_mode):
    if run_mode == MANUAL_MODE or is_in_schedule(9, 2, 0, 18, 0, 0):
        FUND_COMPARE_URL = "https://fund.fipiran.ir/api/v1/fund/fundcompare"

        funds = get_http_response(req_url=FUND_COMPARE_URL, req_headers=FIPIRAN_HEADERS)

        if funds:
            funds = funds.json().get("items")
            mongo_conn = MongodbInterface(
                db_name=FUND_MONGO_DB, collection_name=FUND_ALL_DATA_COLLECTION
            )
            mongo_conn.insert_docs_into_collection(documents=funds)


@shared_task(name="get_all_fund_detail_task", expires=300)
def get_all_fund_detail(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=get_all_fund_detail_main,
        kw_args={"run_mode": run_mode},
    )
