from domestic_market.models import DomesticCommodityType
from rest_framework import serializers


class GetDomesticCommodityTypeSerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticCommodityType
        fields = ["id", "name"]
