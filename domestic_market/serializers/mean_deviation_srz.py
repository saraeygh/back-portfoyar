from core.configs import HEZAR_RIAL_TO_MILLION_TOMAN, HEZAR_RIAL_TO_BILLION_TOMAN
from rest_framework import serializers
from core.serializers import RoundedFloatField


class DomesticMeanDeviationSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    producer = serializers.CharField()
    symbol = serializers.CharField()
    link = serializers.CharField()
    commodity = serializers.CharField()
    commodity_type = serializers.CharField()
    industry = serializers.CharField()
    domestic_mean = RoundedFloatField(decimal_places=2)
    domestic_last_price = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
    deviation = RoundedFloatField(decimal_places=2)
    commodity_sell_percent = RoundedFloatField(decimal_places=2)
    commodity_value_total = RoundedFloatField(decimal_places=0)
    producer_value_total = RoundedFloatField(decimal_places=0)
    unit = serializers.CharField()
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["domestic_mean"] = (
            instance["domestic_mean"] / HEZAR_RIAL_TO_MILLION_TOMAN
        )

        instance["domestic_last_price"] = (
            instance["domestic_last_price"] / HEZAR_RIAL_TO_MILLION_TOMAN
        )

        instance["commodity_value_total"] = (
            instance["commodity_value_total"] / HEZAR_RIAL_TO_BILLION_TOMAN
        )
        instance["producer_value_total"] = (
            instance["producer_value_total"] / HEZAR_RIAL_TO_BILLION_TOMAN
        )

        return super().to_representation(instance)


class SummaryDomesticMeanDeviationSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    producer = serializers.CharField()
    symbol = serializers.CharField()
    link = serializers.CharField()
    commodity = serializers.CharField()
    domestic_mean = RoundedFloatField(decimal_places=2)
    domestic_last_price = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
    deviation = RoundedFloatField(decimal_places=2)
    commodity_sell_percent = RoundedFloatField(decimal_places=2)
    commodity_value_total = RoundedFloatField(decimal_places=0)
    chart = serializers.DictField()

    def to_representation(self, instance):
        instance["domestic_mean"] = (
            instance["domestic_mean"] / HEZAR_RIAL_TO_MILLION_TOMAN
        )

        instance["domestic_last_price"] = (
            instance["domestic_last_price"] / HEZAR_RIAL_TO_MILLION_TOMAN
        )

        instance["commodity_value_total"] = (
            instance["commodity_value_total"] / HEZAR_RIAL_TO_BILLION_TOMAN
        )
        instance["producer_value_total"] = (
            instance["producer_value_total"] / HEZAR_RIAL_TO_BILLION_TOMAN
        )

        return super().to_representation(instance)


class DashboardDomesticMeanDeviationSerailizer(serializers.Serializer):
    symbol = serializers.CharField()
    link = serializers.CharField()
    commodity = serializers.CharField()
    deviation = RoundedFloatField(decimal_places=2)
    last_price_date = serializers.CharField()
