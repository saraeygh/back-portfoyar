import jdatetime
from rest_framework import serializers
from domestic_market.models import DomesticDollarPrice
from core.serializers import RoundedFloatField
from core.configs import HEZAR_RIAL_TO_MILLION_TOMAN


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

        if instance["trade_date"] in dollar_prices_dict:
            dollar_price = dollar_prices_dict[instance["trade_date"]]

        elif DomesticDollarPrice.objects.filter(
            date__lt=instance["trade_date"]
        ).exists():
            dollar_price = (
                DomesticDollarPrice.objects.filter(date__lt=instance["trade_date"])
                .order_by("date")
                .last()
            )

        elif DomesticDollarPrice.objects.all().exists():
            dollar_price = DomesticDollarPrice.objects.all().order_by("date").first()

        else:
            dollar_price = DomesticDollarPrice.objects.create(
                date="2001-03-25",
                date_shamsi="1380-01-05",
                nima=8028,
                azad=8028,
            )

        representation = super().to_representation(instance)
        representation["azad"] = round(
            instance["avg_price"] * 100 / dollar_price.azad, 2
        )
        representation["nima"] = round(
            instance["avg_price"] * 100 / dollar_price.nima, 2
        )

        representation["avg_price"] = round(
            instance["avg_price"] / HEZAR_RIAL_TO_MILLION_TOMAN, 2
        )

        return representation
