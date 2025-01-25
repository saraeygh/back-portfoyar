from tqdm import tqdm

from core.utils import get_http_response

from fund.models import FundType
from . import FIPIRAN_HEADERS


def update_fund_type():
    FUND_TYPE_URL = "https://fund.fipiran.ir/api/v1/fund/fundtype"

    fund_types = get_http_response(req_url=FUND_TYPE_URL, req_headers=FIPIRAN_HEADERS)
    fund_types = fund_types.json().get("items")
    for fund_type in tqdm(fund_types, desc="Updating fund types", ncols=10):
        code = fund_type.get("fundType")
        name = fund_type.get("name")
        is_active = fund_type.get("isActive")

        FundType.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "is_active": is_active,
            },
        )
