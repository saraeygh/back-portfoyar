from global_market.models import GlobalTransit


def get_transit_dict() -> dict:
    all_transit = GlobalTransit.objects.all()

    transit_dict = {}
    for transit in all_transit:
        transit_dict[(transit.transit_type, transit.transit_unit)] = transit.id

    return transit_dict
