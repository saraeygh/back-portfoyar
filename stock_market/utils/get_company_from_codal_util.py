from core.utils import get_http_response
from stock_market.models import CodalCompany
from . import get_existing_company_dict


def get_company_from_codal():
    HEADERS = {
        "Host": "search.codal.ir",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://codal.ir",
        "Connection": "keep-alive",
        "Referer": "https://codal.ir/",
        "Sec-Fetch-Site": "same-site",
    }

    URL = "https://search.codal.ir/api/search/v1/companies"

    company_list = get_http_response(req_url=URL, req_headers=HEADERS)
    try:
        company_list = company_list.json()
    except Exception:
        company_list = []

    existing_company_dict = get_existing_company_dict()
    company_bulk_list = []
    for company in company_list:
        symbol = company["symbol"] = company.pop("sy")

        if symbol in existing_company_dict:
            continue
        else:
            company["codal_id"] = company.pop("i")
            company["name"] = company.pop("n")
            company["publisher_state"] = company.pop("st")
            company["codal_t"] = company.pop("t")
            company["codal_IG"] = company.pop("IG")
            company["codal_RT"] = company.pop("RT")

            new_company = CodalCompany(**company)
            existing_company_dict[symbol] = new_company
            company_bulk_list.append(new_company)

    if company_bulk_list:
        new_created_company = CodalCompany.objects.bulk_create(company_bulk_list)

        for created_company in new_created_company:
            existing_company_dict[created_company.symbol] = created_company

    return existing_company_dict
