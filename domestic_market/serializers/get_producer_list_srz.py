from domestic_market.models import DomesticProducer
from rest_framework import serializers


class GetDomesticProducerListSerailizer(serializers.ModelSerializer):
    class Meta:
        model = DomesticProducer
        fields = ["id", "name"]
