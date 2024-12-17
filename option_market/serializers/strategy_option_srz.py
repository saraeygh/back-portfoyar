from rest_framework import serializers

from option_market.models import StrategyOption


class StrategyOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StrategyOption
        fields = ["sequence", "name", "key", "profit", "desc"]

    def to_representation(self, instance: StrategyOption):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        file_url = (
            f"{request.build_absolute_uri("/strategy-schema/")}{instance.key}.svg"
        )
        representation["schema"] = file_url

        return representation
