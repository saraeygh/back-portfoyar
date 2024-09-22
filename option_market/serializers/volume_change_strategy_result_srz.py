from rest_framework import serializers
from core.serializers import RoundedFloatField


class VolumeChangeStrategyResultSerializer(serializers.Serializer):
    asset_name = serializers.CharField()
    option_group = serializers.CharField()

    on_change_win_rate = RoundedFloatField()
    after_change_win_rate = RoundedFloatField()

    on_change_max_possible_return_percent = RoundedFloatField()
    after_change_max_possible_return_percent = RoundedFloatField()

    on_change_expected_day_of_max_return_percent = serializers.SerializerMethodField()
    after_change_expected_day_of_max_return_percent = (
        serializers.SerializerMethodField()
    )

    def get_on_change_expected_day_of_max_return_percent(self, obj: dict):
        on_change_expected_day_of_max_return_percent = obj.get(
            "on_change_expected_day_of_max_return_percent"
        )

        return round(on_change_expected_day_of_max_return_percent)

    def get_after_change_expected_day_of_max_return_percent(self, obj: dict):
        after_change_expected_day_of_max_return_percent = obj.get(
            "after_change_expected_day_of_max_return_percent"
        )

        return round(after_change_expected_day_of_max_return_percent)
