from domestic_market.models import DomesticDollarPrice
from rest_framework import serializers


class GetDollarPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomesticDollarPrice
        fields = ["id", "date", "date_shamsi", "azad", "nima"]
