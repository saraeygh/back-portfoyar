import jdatetime
from rest_framework import serializers
from core.serializers import RoundedFloatField


class RatioChartSerailizer(serializers.Serializer):
    trade_date = serializers.SerializerMethodField()
    avg_price = RoundedFloatField()
    mean = RoundedFloatField()
    competition = RoundedFloatField()

    def get_trade_date(self, instance):
        gregorian_date = instance["trade_date"]
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

        return str(jalali_date)
