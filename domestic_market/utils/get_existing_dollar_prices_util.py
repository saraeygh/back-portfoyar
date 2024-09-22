from domestic_market.models import DomesticDollarPrice


def get_existing_dollar_prices_dict() -> dict:
    dollar_prices = DomesticDollarPrice.objects.all().order_by("date")

    dollar_prices_dict = {}
    for dollar_price in dollar_prices:
        dollar_prices_dict[dollar_price.date] = dollar_price

    return dollar_prices_dict
