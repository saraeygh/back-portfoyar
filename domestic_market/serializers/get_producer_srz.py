from domestic_market.models import DomesticTrade
from rest_framework import serializers


class GetDomesticProducerSerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticTrade
        fields = ["id", "name"]

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_id(self, instance: DomesticTrade):
        return instance.producer.id

    def get_name(self, instance: DomesticTrade):
        return instance.producer.name
