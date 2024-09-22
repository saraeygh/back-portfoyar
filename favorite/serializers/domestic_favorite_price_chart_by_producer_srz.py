from favorite.models import DomesticFavoritePriceChartByProducer
from rest_framework import serializers


class DomesticAddFavoritePriceChartByProducerSerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticFavoritePriceChartByProducer
        fields = (
            "user",
            "producer",
            "commodity",
            "trade_commodity_name",
        )


class DomesticGetFavoritePriceChartByProducerSerailizer(serializers.ModelSerializer):
    producer_name = serializers.SerializerMethodField()
    commodity_name = serializers.SerializerMethodField()
    trade_commodity_name_name = serializers.SerializerMethodField()

    class Meta:
        model = DomesticFavoritePriceChartByProducer
        fields = (
            "id",
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

        representation["company"] = representation.pop("producer_name")
        representation["company_id"] = representation.pop("producer")

        representation["group"] = representation.pop("commodity_name")
        representation["group_id"] = representation.pop("commodity")

        representation["commodity"] = representation.pop("trade_commodity_name_name")
        representation["commodity_id"] = representation.pop("trade_commodity_name")

        return representation
