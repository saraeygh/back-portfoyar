from favorite.models import GlobalFavoritePriceChart
from rest_framework import serializers


class GlobalAddFavoritePriceChartSerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalFavoritePriceChart
        fields = (
            "user",
            "industry",
            "commodity_type",
            "commodity",
            "transit",
        )


class GlobalGetFavoritePriceChartSerailizer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name")
    commodity_type_name = serializers.CharField(source="commodity_type.name")
    commodity_name = serializers.SerializerMethodField()
    transit_name = serializers.SerializerMethodField()

    class Meta:
        model = GlobalFavoritePriceChart
        fields = (
            "id",
            "user",
            "industry",
            "industry_name",
            "commodity_type",
            "commodity_type_name",
            "commodity",
            "commodity_name",
            "transit",
            "transit_name",
        )

    def get_commodity_name(self, instance):
        if instance.commodity:
            return instance.commodity.name
        return None

    def get_transit_name(self, instance):
        if instance.transit:
            return instance.transit.transit_type
        return None
