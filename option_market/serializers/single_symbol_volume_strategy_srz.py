from rest_framework import serializers
from core.serializers import RoundedFloatField


class SingleSymbolVlomueStrategySerializer(serializers.Serializer):
    asset_name = serializers.CharField()
    symbol = serializers.CharField()

    current_day_date = serializers.CharField()
    current_day_volume = RoundedFloatField()
    current_day_price = RoundedFloatField()

    on_change_day_date = serializers.CharField()
    on_change_day_volume = RoundedFloatField()
    on_change_day_price = RoundedFloatField()

    after_change_day_date = serializers.CharField()
    after_change_day_volume = RoundedFloatField()
    after_change_day_price = RoundedFloatField()

    on_change_return_period_day_date = serializers.CharField()
    on_change_return_period_day_price = RoundedFloatField()
    on_change_period_return = RoundedFloatField()
    on_change_period_return_percent = RoundedFloatField()

    after_change_return_period_day_date = serializers.CharField()
    after_change_return_period_day_price = RoundedFloatField()
    after_change_period_return = RoundedFloatField()
    after_change_period_return_percent = RoundedFloatField()

    on_change_max_comulative_return_percent = RoundedFloatField()
    after_change_max_comulative_return_percent = RoundedFloatField()

    on_change_day_of_max_percent = serializers.IntegerField()
    after_change_day_of_max_percent = serializers.IntegerField()

    on_change_day_of_pass_threshold = serializers.IntegerField()
    after_change_day_of_pass_threshold = serializers.IntegerField()
