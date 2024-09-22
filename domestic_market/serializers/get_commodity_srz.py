from domestic_market.models import DomesticCommodity
from rest_framework import serializers


class GetDomesticCommoditySerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticCommodity
        fields = ["id", "name"]
