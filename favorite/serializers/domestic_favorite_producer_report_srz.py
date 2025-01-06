from rest_framework import serializers
from favorite.models import DomesticFavoriteProducerReport


class DomesticGetFavoriteProducerReportSerailizer(serializers.ModelSerializer):
    producer_name = serializers.SerializerMethodField()

    class Meta:
        model = DomesticFavoriteProducerReport
        fields = ("id", "producer", "producer_name")

    def get_producer_name(self, instance):
        if instance.producer:
            return instance.producer.name

        return ""
