from core.configs import FUND_MONGO_DB, FUND_ALL_DATA_COLLECTION
from core.utils import MongodbInterface, get_http_response, run_main_task

from fund.utils import FIPIRAN_HEADERS


def get_all_fund_detail_main():
    FUND_COMPARE_URL = "https://fund.fipiran.ir/api/v1/fund/fundcompare"

    funds = get_http_response(req_url=FUND_COMPARE_URL, req_headers=FIPIRAN_HEADERS)

    if funds:
        funds = funds.json().get("items")
        mongo_conn = MongodbInterface(
            db_name=FUND_MONGO_DB, collection_name=FUND_ALL_DATA_COLLECTION
        )
        mongo_conn.insert_docs_into_collection(documents=funds)
        mongo_conn.client.close()


def get_all_fund_detail():

    run_main_task(
        main_task=get_all_fund_detail_main,
    )
