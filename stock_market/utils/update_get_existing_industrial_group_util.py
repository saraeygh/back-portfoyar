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

    ig_bulk_update = []
    for group in industry_group:
        code = int(group.get("code"))
        name = (group.get("name")).strip()
        priority = IG_PRIORITY.get(code, 99)
        try:
            ig = StockIndustrialGroup.objects.get(code=code)
            ig.name = name
            ig.priority = priority
            ig_bulk_update.append(ig)
        except StockIndustrialGroup.DoesNotExist:
            StockIndustrialGroup.objects.create(code=code, name=name, priority=priority)

    if ig_bulk_update:
        StockIndustrialGroup.objects.bulk_update(
            objs=ig_bulk_update, fields=["name", "priority"]
        )

    replace_all_arabic_letters_in_db()


IG_PRIORITY = {
    27: 1,
    44: 2,
    43: 3,
    68: 4,
    72: 5,
    34: 6,
    57: 7,
    53: 8,
    40: 9,
    42: 10,
    73: 11,
    31: 12,
    65: 13,
    29: 14,
    38: 15,
    61: 16,
    49: 17,
    56: 18,
    26: 19,
    10: 20,
    11: 21,
    13: 22,
    22: 23,
    1: 24,
    58: 25,
    71: 26,
    74: 27,
    45: 28,
    17: 29,
    28: 30,
    93: 31,
    64: 32,
    32: 33,
    14: 34,
    46: 35,
    51: 36,
    55: 37,
    60: 38,
    20: 39,
    21: 40,
    41: 41,
    90: 42,
    82: 43,
    23: 44,
    19: 45,
    54: 46,
    52: 47,
    50: 48,
    47: 49,
    36: 50,
    35: 51,
    33: 52,
    67: 53,
    66: 54,
    63: 55,
    98: 56,
    76: 57,
    70: 58,
    69: 59,
    39: 60,
    59: 61,
    15: 62,
    24: 63,
}
