from global_market.models import GlobalIndustry

from . import get_industry_dict
from tqdm import tqdm


def populate_industry(global_market_data: list) -> dict:
    existing_industry = get_industry_dict()

    new_industry_bulk = []
    for row in tqdm(global_market_data, desc="Updating industries", ncols=10):
        if row["industry"] not in existing_industry:
            new_industry = GlobalIndustry(name=row["industry"])
            new_industry_bulk.append(new_industry)
            existing_industry[row["industry"]] = "Not_saved"

    if new_industry_bulk:
        new_industry_instances = GlobalIndustry.objects.bulk_create(new_industry_bulk)

        for new_instance in tqdm(
            new_industry_instances, desc="Updating existing industries", ncols=10
        ):
            existing_industry[new_instance.name] = new_instance.id

    return existing_industry
