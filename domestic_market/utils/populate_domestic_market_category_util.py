import json
from tqdm import tqdm
from core.utils import get_http_response
from domestic_market.models import (
    DomesticCommodity,
    DomesticCommodityType,
    DomesticIndustry,
)

HEADERS = {
    "Host": "www.ime.co.ir",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "12",
    "Origin": "https://www.ime.co.ir",
    "Connection": "keep-alive",
    "Referer": "https://www.ime.co.ir/offer-stat.html",
    "Cookie": "ASP.NET_SessionId=zebwrt1sbsuvpw30ze4wgub3; SiteBikeLoadBanacer=9609d25e7d6e5b16cafdd45c3cf1d1ebdb204366ac7135985c4cd71dffa8dd38",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
}


def get_industry():
    PAYLOAD = {"Language": 8}
    INDUSTRY_URL = (
        "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetMainGroups"
    )

    response = get_http_response(
        req_method="POST", req_url=INDUSTRY_URL, req_headers=HEADERS, req_json=PAYLOAD
    )

    industry = response.content.decode()
    industry = json.loads(industry)
    industry = industry.get("d")
    industry_list_of_dict = json.loads(industry)

    return industry_list_of_dict


def populate_industry(industries: list):
    industry_bulk_create = []
    industry_bulk_update = []
    for industry in industries:
        code = industry.get("code")
        name = industry.get("Name")
        try:
            ex_industry = DomesticIndustry.objects.get(code=code)
            if ex_industry.name != name:
                ex_industry.name = name
                industry_bulk_update.append(ex_industry)

        except DomesticIndustry.DoesNotExist:
            new_industry = DomesticIndustry(code=code, name=name)
            industry_bulk_create.append(new_industry)

    if industry_bulk_create:
        DomesticIndustry.objects.bulk_create(industry_bulk_create)

    if industry_bulk_update:
        DomesticIndustry.objects.bulk_update(industry_bulk_update, ["name"])


def get_commodity_type(main_cat_code: int):
    PAYLOAD = {"Language": 8, "MainCat": main_cat_code}
    COMMODITY_TYPE_URL = (
        "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetCatGroups"
    )

    response = get_http_response(
        req_method="POST",
        req_url=COMMODITY_TYPE_URL,
        req_headers=HEADERS,
        req_json=PAYLOAD,
    )

    commodity_type = response.content.decode()
    commodity_type = json.loads(commodity_type)
    commodity_type = commodity_type.get("d")
    commodity_type_list_of_dict = json.loads(commodity_type)

    return commodity_type_list_of_dict


def populate_commodity_type(main_cat_code: int, commodity_types: list):
    industry = DomesticIndustry.objects.get(code=main_cat_code)

    commodity_type_bulk_create = []
    commodity_type_bulk_update = []
    for commodity_type in commodity_types:
        code = commodity_type.get("code")
        name = commodity_type.get("name")
        try:
            ex_commodity_type = DomesticCommodityType.objects.get(code=code)
            if ex_commodity_type.name != name:
                ex_commodity_type.name = name
                commodity_type_bulk_update.append(ex_commodity_type)

        except DomesticCommodityType.DoesNotExist:
            new_commodity_type = DomesticCommodityType(
                industry=industry, name=name, code=code
            )
            commodity_type_bulk_create.append(new_commodity_type)

    if commodity_type_bulk_create:
        DomesticCommodityType.objects.bulk_create(commodity_type_bulk_create)

    if commodity_type_bulk_update:
        DomesticCommodityType.objects.bulk_update(commodity_type_bulk_update, ["name"])


def get_commodity(main_cat_code: int, cat_code: int):
    PAYLOAD = {"Language": 8, "MainCat": main_cat_code, "Cat": cat_code}
    COMMODITY_URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetSubCatGroups"

    response = get_http_response(
        req_method="POST",
        req_url=COMMODITY_URL,
        req_headers=HEADERS,
        req_json=PAYLOAD,
    )

    commodity = response.content.decode()
    commodity = json.loads(commodity)
    commodity = commodity.get("d")
    commodity_list_of_dict = json.loads(commodity)

    return commodity_list_of_dict


def populate_commodity(cat_code: int, commodities: list):
    commodity_type = DomesticCommodityType.objects.get(code=cat_code)

    commodity_bulk_create = []
    commodity_bulk_update = []
    for commodity in commodities:
        code = commodity.get("code")
        name = commodity.get("name")
        try:
            ex_commodity = DomesticCommodity.objects.get(code=code)
            if ex_commodity.name != name:
                ex_commodity.name = name
                commodity_bulk_update.append(ex_commodity)

        except DomesticCommodity.DoesNotExist:
            new_commodity = DomesticCommodity(
                commodity_type=commodity_type, name=name, code=code
            )
            commodity_bulk_create.append(new_commodity)

    if commodity_bulk_create:
        DomesticCommodity.objects.bulk_create(commodity_bulk_create)

    if commodity_bulk_update:
        DomesticCommodity.objects.bulk_update(commodity_bulk_update, ["name"])


def populate_domestic_market_category():
    industry_list = get_industry()
    populate_industry(industries=industry_list)

    main_cat_list = [industry.get("code") for industry in industry_list]
    for main_cat_code in tqdm(main_cat_list, desc="Main categories", ncols=10):
        commodity_type_list = get_commodity_type(main_cat_code=main_cat_code)
        populate_commodity_type(
            main_cat_code=main_cat_code, commodity_types=commodity_type_list
        )

        cat_list = [
            commodity_type.get("code") for commodity_type in commodity_type_list
        ]
        for cat_code in cat_list:
            commodity_list = get_commodity(
                main_cat_code=main_cat_code, cat_code=cat_code
            )
            populate_commodity(cat_code=cat_code, commodities=commodity_list)
