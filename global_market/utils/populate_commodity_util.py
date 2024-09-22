from global_market.models import GlobalCommodity

from . import get_commodity_dict
from tqdm import tqdm


def populate_commodity(global_market_data: list, existing_commodity_type: dict) -> dict:
    existing_commodity = get_commodity_dict()

    new_commodity_bulk = []
    for row in tqdm(global_market_data, desc="Updating commodities", ncols=10):
        if (row["commodity"], row["commodity_type"]) not in existing_commodity:
            commodity_type_id = existing_commodity_type.get(
                (row["commodity_type"], row["industry"])
            )

            new_commodity = GlobalCommodity(
                commodity_type_id=commodity_type_id, name=row["commodity"]
            )
            new_commodity_bulk.append(new_commodity)

            existing_commodity[(row["commodity"], row["commodity_type"])] = "Not_saved"

    if new_commodity_bulk:
        new_commodity_instances = GlobalCommodity.objects.bulk_create(
            new_commodity_bulk
        )

        for new_instance in tqdm(
            new_commodity_instances, desc="Updating existing commodities", ncols=10
        ):
            existing_commodity[
                (new_instance.name, new_instance.commodity_type.name)
            ] = new_instance.id

    return existing_commodity
