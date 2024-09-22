from favorite.models import GlobalFavoriteRatioChart
from rest_framework import serializers


class GlobalAddFavoriteRatioChartSerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalFavoriteRatioChart
        fields = (
            "user",
            "industry_1",
            "commodity_type_1",
            "commodity_1",
            "transit_1",
            "industry_2",
            "commodity_type_2",
            "commodity_2",
            "transit_2",
        )


class GlobalGetFavoriteRatioChartSerailizer(serializers.ModelSerializer):
    industry_1_name = serializers.CharField(source="industry_1.name")
    commodity_type_1_name = serializers.CharField(source="commodity_type_1.name")
    commodity_1_name = serializers.SerializerMethodField()
    transit_1_name = serializers.SerializerMethodField()

    industry_2_name = serializers.CharField(source="industry_2.name")
    commodity_type_2_name = serializers.CharField(source="commodity_type_2.name")
    commodity_2_name = serializers.SerializerMethodField()
    transit_2_name = serializers.SerializerMethodField()

    class Meta:
        model = GlobalFavoriteRatioChart
        fields = (
            "id",
            "user",
            "industry_1",
            "industry_1_name",
            "commodity_type_1",
            "commodity_type_1_name",
            "commodity_1",
            "commodity_1_name",
            "transit_1",
            "transit_1_name",
            "industry_2",
            "industry_2_name",
            "commodity_type_2",
            "commodity_type_2_name",
            "commodity_2",
            "commodity_2_name",
            "transit_2",
            "transit_2_name",
        )

    def get_commodity_1_name(self, instance):
        if instance.commodity_1:
            return instance.commodity_1.name
        return None

    def get_transit_1_name(self, instance):
        if instance.transit_1:
            return instance.transit_1.transit_type
        return None

    def get_commodity_2_name(self, instance):
        if instance.commodity_2:
            return instance.commodity_2.name
        return None

    def get_transit_2_name(self, instance):
        if instance.transit_2:
            return instance.transit_2.transit_type
        return None
