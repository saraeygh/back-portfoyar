import json
from tqdm import tqdm
from core.utils import get_http_response
from domestic_market.models import (
    DomesticCommodity,
    DomesticCommodityType,
    DomesticIndustry,
)


def get_existing_industry():
    existing_industry = DomesticIndustry.objects.all().values(
        "id",
        "name",
        "code",
    )

    existing_industry_dict = {}
    for industry in existing_industry:
        existing_industry_dict[(industry.get("name"), industry.get("code"))] = (
            industry.get("id")
        )

    return existing_industry_dict


def get_industry():
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
    PAYLOAD = {"Language": 8}
    INDUSTRY_URL = (
        "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetMainGroups"
    )

    response = get_http_response(
        req_method="POST", req_url=INDUSTRY_URL, req_headers=HEADERS, req_json=PAYLOAD
    )

    try:
        industry = response.content.decode()
        industry = json.loads(industry)
        industry = industry.get("d")
        industry_list_of_dict = json.loads(industry)
    except Exception:
        return []

    return industry_list_of_dict


def populate_industry(industries: list):
    existing_industry_dict = get_existing_industry()

    industry_bulk_list = []
    for industry in industries:
        name = industry.get("Name")
        code = industry.get("code")
        if (name, code) not in existing_industry_dict:
            new_industry = DomesticIndustry(name=name, code=code)
            industry_bulk_list.append(new_industry)

    if industry_bulk_list:
        created_industry = DomesticIndustry.objects.bulk_create(industry_bulk_list)
    else:
        created_industry = []

    if created_industry:
        for industry in created_industry:
            existing_industry_dict[(industry.name, industry.code)] = industry.id

    return existing_industry_dict


def get_existing_commodity_type():
    existing_commodity_type = DomesticCommodityType.objects.all().values(
        "id",
        "industry_id",
        "name",
        "code",
    )

    existing_commodity_type_dict = {}
    for commodity_type in existing_commodity_type:
        existing_commodity_type_dict[
            (
                commodity_type.get("industry_id"),
                commodity_type.get("name"),
                commodity_type.get("code"),
            )
        ] = commodity_type.get("id")

    return existing_commodity_type_dict


def get_commodity_type(main_cat_code: int):
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

    try:
        commodity_type = response.content.decode()
        commodity_type = json.loads(commodity_type)
        commodity_type = commodity_type.get("d")
        commodity_type_list_of_dict = json.loads(commodity_type)
    except Exception:
        return []

    return commodity_type_list_of_dict


def populate_commodity_type(main_cat_code: int, commodity_types: list):
    existing_commodity_type_dict = get_existing_commodity_type()
    industry_id = DomesticIndustry.objects.filter(code=main_cat_code).first().id

    commodity_type_bulk_list = []
    for commodity_type in commodity_types:
        name = commodity_type.get("name")
        code = commodity_type.get("code")
        if (industry_id, name, code) not in existing_commodity_type_dict:
            new_commodity_type = DomesticCommodityType(
                industry_id=industry_id, name=name, code=code
            )
            commodity_type_bulk_list.append(new_commodity_type)

    if commodity_type_bulk_list:
        created_commodity_type = DomesticCommodityType.objects.bulk_create(
            commodity_type_bulk_list
        )
    else:
        created_commodity_type = []

    if created_commodity_type:
        for commodity_type in created_commodity_type:
            existing_commodity_type_dict[
                (commodity_type.industry.id, commodity_type.name, commodity_type.code)
            ] = commodity_type.id

    return existing_commodity_type_dict


def get_existing_commodity():
    existing_commodity = DomesticCommodity.objects.all().values(
        "id",
        "commodity_type_id",
        "name",
        "code",
    )

    existing_commodity_dict = {}
    for commodity in existing_commodity:
        existing_commodity_dict[
            (
                commodity.get("commodity_type_id"),
                commodity.get("name"),
                commodity.get("code"),
            )
        ] = commodity.get("id")

    return existing_commodity_dict


def get_commodity(main_cat_code: int, cat_code: int):
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
    PAYLOAD = {"Language": 8, "MainCat": main_cat_code, "Cat": cat_code}
    COMMODITY_URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetSubCatGroups"

    response = get_http_response(
        req_method="POST",
        req_url=COMMODITY_URL,
        req_headers=HEADERS,
        req_json=PAYLOAD,
    )

    try:
        commodity = response.content.decode()
        commodity = json.loads(commodity)
        commodity = commodity.get("d")
        commodity_list_of_dict = json.loads(commodity)
    except Exception:
        return []

    return commodity_list_of_dict


def populate_commodity(cat_code: int, commodities: list):
    existing_commodity_dict = get_existing_commodity()
    commodity_type_id = DomesticCommodityType.objects.filter(code=cat_code).first().id

    commodity_bulk_list = []
    for commodity in commodities:
        name = commodity.get("name")
        code = commodity.get("code")
        if (commodity_type_id, name, code) not in existing_commodity_dict:
            new_commodity = DomesticCommodity(
                commodity_type_id=commodity_type_id, name=name, code=code
            )
            commodity_bulk_list.append(new_commodity)

    if commodity_bulk_list:
        created_commodity = DomesticCommodity.objects.bulk_create(commodity_bulk_list)
    else:
        created_commodity = []

    if created_commodity:
        for commodity in created_commodity:
            existing_commodity_dict[
                (commodity.commodity_type.id, commodity.name, commodity.code)
            ] = commodity.id

    return existing_commodity_dict


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
