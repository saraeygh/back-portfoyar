from global_market.models import GlobalIndustry


def get_industry_dict() -> dict:
    all_industry = GlobalIndustry.objects.all()

    industry_dict = {}
    for industry in all_industry:
        industry_dict[industry.name] = industry.id

    return industry_dict
