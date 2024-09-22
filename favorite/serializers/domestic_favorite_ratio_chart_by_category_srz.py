from rest_framework import serializers
from favorite.models import DomesticFavoriteRatioChartByCategory


class DomesticAddFavoriteRatioChartByCategorySerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticFavoriteRatioChartByCategory
        fields = (
            "user",
            "industry_1",
            "commodity_type_1",
            "commodity_1",
            "producer_1",
            "trade_commodity_name_1",
            "industry_2",
            "commodity_type_2",
            "commodity_2",
            "producer_2",
            "trade_commodity_name_2",
        )


class DomesticGetFavoriteRatioChartByCategorySerailizer(serializers.ModelSerializer):
    industry_1_name = serializers.CharField(source="industry_1.name")
    commodity_type_1_name = serializers.CharField(source="commodity_type_1.name")
    commodity_1_name = serializers.SerializerMethodField()
    producer_1_name = serializers.SerializerMethodField()
    trade_commodity_name_1_name = serializers.SerializerMethodField()

    industry_2_name = serializers.CharField(source="industry_2.name")
    commodity_type_2_name = serializers.CharField(source="commodity_type_2.name")
    commodity_2_name = serializers.SerializerMethodField()
    producer_2_name = serializers.SerializerMethodField()
    trade_commodity_name_2_name = serializers.SerializerMethodField()

    class Meta:
        model = DomesticFavoriteRatioChartByCategory
        fields = (
            "id",
            "industry_1",
            "industry_1_name",
            "commodity_type_1",
            "commodity_type_1_name",
            "commodity_1",
            "commodity_1_name",
            "producer_1",
            "producer_1_name",
            "trade_commodity_name_1",
            "trade_commodity_name_1_name",
            "industry_2",
            "industry_2_name",
            "commodity_type_2",
            "commodity_type_2_name",
            "commodity_2",
            "commodity_2_name",
            "producer_2",
            "producer_2_name",
            "trade_commodity_name_2",
            "trade_commodity_name_2_name",
        )

    def get_commodity_1_name(self, instance):
        if instance.commodity_1:
            return instance.commodity_1.name
        return None

    def get_producer_1_name(self, instance):
        if instance.producer_1:
            return instance.producer_1.name
        return None

    def get_commodity_2_name(self, instance):
        if instance.commodity_2:
            return instance.commodity_2.name
        return None

    def get_producer_2_name(self, instance):
        if instance.producer_2:
            return instance.producer_2.name
        return None

    def get_trade_commodity_name_1_name(self, instance):
        if instance.trade_commodity_name_1:
            return instance.trade_commodity_name_1.commodity_name
        return None

    def get_trade_commodity_name_2_name(self, instance):
        if instance.trade_commodity_name_2:
            return instance.trade_commodity_name_2.commodity_name
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["industry1_id"] = representation.pop("industry_1")
        representation["industry1"] = representation.pop("industry_1_name")

        representation["field1_id"] = representation.pop("commodity_type_1")
        representation["field1"] = representation.pop("commodity_type_1_name")

        representation["company1_id"] = representation.pop("producer_1")
        representation["company1"] = representation.pop("producer_1_name")

        representation["group1_id"] = representation.pop("commodity_1")
        representation["group1"] = representation.pop("commodity_1_name")

        representation["commodity1_id"] = representation.pop("trade_commodity_name_1")
        representation["commodity1"] = representation.pop("trade_commodity_name_1_name")

        representation["industry2_id"] = representation.pop("industry_2")
        representation["industry2"] = representation.pop("industry_2_name")

        representation["field2_id"] = representation.pop("commodity_type_2")
        representation["field2"] = representation.pop("commodity_type_2_name")

        representation["company2_id"] = representation.pop("producer_2")
        representation["company2"] = representation.pop("producer_2_name")

        representation["group2_id"] = representation.pop("commodity_2")
        representation["group2"] = representation.pop("commodity_2_name")

        representation["commodity2_id"] = representation.pop("trade_commodity_name_2")
        representation["commodity2"] = representation.pop("trade_commodity_name_2_name")

        return representation
