import jdatetime

from rest_framework import serializers

from core.serializers import RoundedFloatField
from core.configs import HEZAR_RIAL_TO_MILLION_TOMAN

from domestic_market.models import DomesticDollarPrice


class PriceChartSerailizer(serializers.Serializer):
    trade_date = serializers.SerializerMethodField()
    avg_price = RoundedFloatField()
    competition = RoundedFloatField()

    def get_trade_date(self, instance):
        gregorian_date = instance["trade_date"]
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

        return str(jalali_date)

    def to_representation(self, instance):
        dollar_prices_dict = self.context.get("existing_dollar_prices")

        last_dollar = (
            DomesticDollarPrice.objects.filter(date__lt=instance["trade_date"])
            .order_by("date")
            .last()
        )
        any_dollar = DomesticDollarPrice.objects.all().order_by("date").first()

        if instance["trade_date"] in dollar_prices_dict:
            dollar_price = dollar_prices_dict[instance["trade_date"]]
        elif last_dollar:
            dollar_price = last_dollar
        elif any_dollar:
            dollar_price = any_dollar
        else:
            dollar_price = DomesticDollarPrice.objects.create(
                date="2001-03-25", date_shamsi="1380-01-05", nima=8028, azad=8028
            )

        representation = super().to_representation(instance)
        representation["azad"] = round(
            instance["avg_price"] * 1000 / dollar_price.azad, 2
        )
        representation["nima"] = round(
            instance["avg_price"] * 1000 / dollar_price.nima, 2
        )

        representation["avg_price"] = round(
            instance["avg_price"] / HEZAR_RIAL_TO_MILLION_TOMAN, 2
        )

        return representation
