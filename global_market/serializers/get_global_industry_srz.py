from global_market.models import GlobalIndustry
from rest_framework import serializers


class GetGlobalIndustrySerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalIndustry
        fields = ["id", "name"]
