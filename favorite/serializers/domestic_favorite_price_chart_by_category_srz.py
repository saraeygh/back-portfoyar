from rest_framework import serializers
from favorite.models import DomesticFavoritePriceChartByCategory


class DomesticAddFavoritePriceChartByCategorySerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticFavoritePriceChartByCategory
        fields = (
            "user",
            "industry",
            "commodity_type",
            "commodity",
            "producer",
            "trade_commodity_name",
        )


class DomesticGetFavoritePriceChartByCategorySerailizer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name")
    commodity_type_name = serializers.CharField(source="commodity_type.name")
    commodity_name = serializers.SerializerMethodField()
    producer_name = serializers.SerializerMethodField()
    trade_commodity_name_name = serializers.SerializerMethodField()

    class Meta:
        model = DomesticFavoritePriceChartByCategory
        fields = (
            "id",
            "industry",
            "industry_name",
            "commodity_type",
            "commodity_type_name",
            "producer",
            "producer_name",
            "commodity",
            "commodity_name",
            "trade_commodity_name",
            "trade_commodity_name_name",
        )

    def get_commodity_name(self, instance):
        if instance.commodity:
            return instance.commodity.name
        return None

    def get_producer_name(self, instance):
        if instance.producer:
            return instance.producer.name
        return None

    def get_trade_commodity_name_name(self, instance):
        if instance.trade_commodity_name:
            return instance.trade_commodity_name.commodity_name
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["industry_id"] = representation.pop("industry")
        representation["industry"] = representation.pop("industry_name")

        representation["field_id"] = representation.pop("commodity_type")
        representation["field"] = representation.pop("commodity_type_name")

        representation["group_id"] = representation.pop("commodity")
        representation["group"] = representation.pop("commodity_name")

        representation["company_id"] = representation.pop("producer")
        representation["company"] = representation.pop("producer_name")

        representation["commodity_id"] = representation.pop("trade_commodity_name")
        representation["commodity"] = representation.pop("trade_commodity_name_name")

        return representation
