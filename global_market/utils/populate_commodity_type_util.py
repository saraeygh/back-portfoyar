from global_market.models import GlobalCommodityType

from . import get_commodity_type_dict
from tqdm import tqdm


def populate_commodity_type(global_market_data: list, existing_industry: dict) -> dict:
    existing_commodity_type = get_commodity_type_dict()

    new_commodity_type_bulk = []
    for row in tqdm(global_market_data, desc="Updating commodity types", ncols=10):
        if (row["commodity_type"], row["industry"]) not in existing_commodity_type:
            industry_id = existing_industry.get(row["industry"])

            new_commodity_type = GlobalCommodityType(
                industry_id=industry_id, name=row["commodity_type"]
            )

            new_commodity_type_bulk.append(new_commodity_type)
            existing_commodity_type[(row["commodity_type"], row["industry"])] = (
                "Not_saved"
            )

    if new_commodity_type_bulk:
        new_commodity_type_instances = GlobalCommodityType.objects.bulk_create(
            new_commodity_type_bulk
        )

        for new_instance in tqdm(
            new_commodity_type_instances,
            desc="Updating existing commodity types",
            ncols=10,
        ):
            existing_commodity_type[(new_instance.name, new_instance.industry.name)] = (
                new_instance.id
            )

    return existing_commodity_type
