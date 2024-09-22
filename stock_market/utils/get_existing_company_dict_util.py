from stock_market.models import CodalCompany


def get_existing_company_dict():
    company_list = CodalCompany.objects.all()

    existing_company_dict = {}
    for company in company_list:
        existing_company_dict[company.symbol] = company

    return existing_company_dict
