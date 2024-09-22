from favorite.models import DomesticFavoriteRatioChartByProducer
from rest_framework import serializers


class DomesticAddFavoriteRatioChartByProducerSerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticFavoriteRatioChartByProducer
        fields = (
            "user",
            "producer_1",
            "commodity_1",
            "trade_commodity_name_1",
            "producer_2",
            "commodity_2",
            "trade_commodity_name_2",
        )


class DomesticGetFavoriteRatioChartByProducerSerailizer(serializers.ModelSerializer):
    producer_1_name = serializers.SerializerMethodField()
    commodity_1_name = serializers.SerializerMethodField()
    trade_commodity_name_1_name = serializers.SerializerMethodField()

    producer_2_name = serializers.SerializerMethodField()
    commodity_2_name = serializers.SerializerMethodField()
    trade_commodity_name_2_name = serializers.SerializerMethodField()

    class Meta:
        model = DomesticFavoriteRatioChartByProducer
        fields = (
            "id",
            "producer_1",
            "producer_1_name",
            "commodity_1",
            "commodity_1_name",
            "trade_commodity_name_1",
            "trade_commodity_name_1_name",
            "producer_2",
            "producer_2_name",
            "commodity_2",
            "commodity_2_name",
            "trade_commodity_name_2",
            "trade_commodity_name_2_name",
        )

    def get_producer_1_name(self, instance):
        if instance.producer_1:
            return instance.producer_1.name
        return None

    def get_commodity_1_name(self, instance):
        if instance.commodity_1:
            return instance.commodity_1.name
        return None

    def get_producer_2_name(self, instance):
        if instance.producer_2:
            return instance.producer_2.name
        return None

    def get_commodity_2_name(self, instance):
        if instance.commodity_2:
            return instance.commodity_2.name
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

        representation["company1"] = representation.pop("producer_1_name")
        representation["company1_id"] = representation.pop("producer_1")

        representation["group1"] = representation.pop("commodity_1_name")
        representation["group1_id"] = representation.pop("commodity_1")

        representation["commodity1"] = representation.pop("trade_commodity_name_1_name")
        representation["commodity1_id"] = representation.pop("trade_commodity_name_1")

        representation["company2"] = representation.pop("producer_2_name")
        representation["company2_id"] = representation.pop("producer_2")

        representation["group2"] = representation.pop("commodity_2_name")
        representation["group2_id"] = representation.pop("commodity_2")

        representation["commodity2"] = representation.pop("trade_commodity_name_2_name")
        representation["commodity2_id"] = representation.pop("trade_commodity_name_2")

        return representation
