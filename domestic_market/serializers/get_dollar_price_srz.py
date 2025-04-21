from domestic_market.models import DomesticDollarPrice
from rest_framework import serializers


class GetDollarPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticDollarPrice
        fields = ["id", "date", "date_shamsi", "azad", "nima"]

    def to_representation(self, instance: DomesticDollarPrice):
        instance.date_shamsi = instance.date_shamsi.replace("-", "/")

        return super().to_representation(instance)
