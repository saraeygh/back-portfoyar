from global_market.models import GlobalTrade
from rest_framework import serializers


class GetGlobalTransitSerailizer(serializers.ModelSerializer):
    class Meta:
        model = GlobalTrade
        fields = ["id", "name"]

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_id(self, instance: GlobalTrade):
        return instance.transit.id

    def get_name(self, instance: GlobalTrade):
        return instance.transit.transit_type
