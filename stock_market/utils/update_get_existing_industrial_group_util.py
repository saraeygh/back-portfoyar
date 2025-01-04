import pandas as pd

from core.utils import (
    TSETMC_REQUEST_HEADERS,
    get_http_response,
    replace_all_arabic_letters_in_db,
)

from stock_market.models import StockIndustrialGroup


URL = "https://cdn.tsetmc.com/api/StaticData/GetStaticData"


def update_get_existing_industrial_group():
    industry_group = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
    industry_group = industry_group.json()
    industry_group = pd.DataFrame(industry_group.get("staticData", []))
    industry_group = industry_group[industry_group["type"] == "IndustrialGroup"]
    industry_group = industry_group.to_dict(orient="records")

    for group in industry_group:
        code = group.get("code")
        name = (group.get("name")).strip()
        try:
            StockIndustrialGroup.objects.get(code=code)
        except StockIndustrialGroup.DoesNotExist:
            StockIndustrialGroup.objects.create(code=code, name=name)

    replace_all_arabic_letters_in_db()
