from global_market.models import GlobalTransit

from . import get_transit_dict
from tqdm import tqdm


def populate_transit(global_market_data: list) -> dict:
    existing_transit = get_transit_dict()

    new_transit_bulk = []
    for row in tqdm(global_market_data, desc="Updating transits", ncols=10):
        if (row["transit"], row["unit"]) not in existing_transit:
            new_transit = GlobalTransit(
                transit_type=row["transit"], transit_unit=row["unit"]
            )
            new_transit_bulk.append(new_transit)

            existing_transit[(row["transit"], row["unit"])] = "Not_saved"

    if new_transit_bulk:
        new_transit_instances = GlobalTransit.objects.bulk_create(new_transit_bulk)

        for new_instance in tqdm(
            new_transit_instances, desc="Updating existing transits", ncols=10
        ):
            existing_transit[(new_instance.transit_type, new_instance.transit_unit)] = (
                new_instance.id
            )

    return existing_transit
