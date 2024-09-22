from domestic_market.models import DomesticIndustry
from rest_framework import serializers


class GetDomesticIndustrySerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticIndustry
        fields = ["id", "name"]
