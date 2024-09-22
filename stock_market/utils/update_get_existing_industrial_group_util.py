import pandas as pd
from core.utils import get_http_response, replace_all_arabic_letters_in_db
from stock_market.models import StockIndustrialGroup
from .used_dicts_util import TSETMC_REQUEST_HEADERS


URL = "https://cdn.tsetmc.com/api/StaticData/GetStaticData"


def update_get_existing_industrial_group():
    industrial_group_list = StockIndustrialGroup.objects.all()

    existing_industrial_group_dict = dict()
    for industrial_group in industrial_group_list:
        existing_industrial_group_dict[industrial_group.code] = industrial_group
    del industrial_group_list

    response = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
    try:
        response = response.json()
        response = response.get("staticData")
    except Exception:
        response = []

    if response:
        industrial_group = pd.DataFrame(response)
        del response
        industrial_group = industrial_group[
            industrial_group["type"] == "IndustrialGroup"
        ]

        industrial_group = industrial_group.to_dict(orient="records")

        industrial_group_bulk_list = []
        for group in industrial_group:
            code = group.get("code")
            name: str = group.get("name")
            name = name.strip()

            if code not in existing_industrial_group_dict:
                new_group = StockIndustrialGroup(code=code, name=name)
                industrial_group_bulk_list.append(new_group)
                existing_industrial_group_dict[code] = new_group

        if industrial_group_bulk_list:
            StockIndustrialGroup.objects.bulk_create(industrial_group_bulk_list)

    replace_all_arabic_letters_in_db()
    return existing_industrial_group_dict
