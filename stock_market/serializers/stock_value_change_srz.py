from rest_framework import serializers
from core.serializers import RoundedFloatField

VALUE_CHANGE_X_TITLE = "تاریخ"
VALUE_CHANGE_Y_TITLE = "ارزش معاملات (میلیارد تومان)"
VALUE_CHANGE_CHART_TITLE = "روند تغییرات ۳۰ روز گذشته ارزش معاملات نماد"


class StockValueChangeSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_update = serializers.CharField()
    mean = RoundedFloatField(decimal_places=2)
    value = RoundedFloatField(decimal_places=2)
    value_change = RoundedFloatField(decimal_places=1)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField(decimal_places=2)
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": VALUE_CHANGE_X_TITLE,
            "y_title": VALUE_CHANGE_Y_TITLE,
            "chart_title": VALUE_CHANGE_CHART_TITLE + " " + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)
