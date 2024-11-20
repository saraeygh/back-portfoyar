from rest_framework import serializers
from core.serializers import RoundedFloatField

MARKET_WATCH_X_TITLE = "زمان"
market_watch_y_title_dict = {
    "money_flow": "ورود پول حقیقی (میلیارد تومان)",
    "buy_pressure": "شاخص قدرت خرید حقیقی",
    "buy_value": "ارزش سرانه خرید حقیقی (میلیارد تومان)",
    "buy_ratio": "نسبت ارزش سفارش‌های خرید به ارزش معاملات",
    "sell_ratio": "نسبت ارزش سفارش‌های فروش به ارزش معاملات",
}
market_watch_chart_title_dict = {
    "money_flow": "روند تغییرات امروز شاخص ورود پول حقیقی برای نماد",
    "buy_pressure": "روند تغییرات امروز شاخص قدرت خرید حقیقی برای نماد",
    "buy_value": "روند تغییرات امروز شاخص ارزش سرانه خرید حقیقی برای نماد",
    "buy_ratio": "روند تغییرات امروز نسبت ارزش‌ سفارش‌های خرید به ارزش معاملات برای نماد",
    "sell_ratio": "روند تغییرات امروز نسبت ارزش‌ سفارش‌های فروش به ارزش معاملات برای نماد",
}


class SummaryPersonMoneyFlowSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    money_flow = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("money_flow"),
            "chart_title": market_watch_chart_title_dict.get("money_flow")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class PersonMoneyFlowSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    money_flow = RoundedFloatField()
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("money_flow"),
            "chart_title": market_watch_chart_title_dict.get("money_flow")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SummaryPersonBuyPressureSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    buy_pressure = RoundedFloatField(decimal_places=1)
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_pressure"),
            "chart_title": market_watch_chart_title_dict.get("buy_pressure")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class PersonBuyPressureSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_pressure = RoundedFloatField(decimal_places=1)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_pressure"),
            "chart_title": market_watch_chart_title_dict.get("buy_pressure")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SummaryPersonBuyValueSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    buy_value = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_value"),
            "chart_title": market_watch_chart_title_dict.get("buy_value")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class PersonBuyValueSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_value = RoundedFloatField()
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_value"),
            "chart_title": market_watch_chart_title_dict.get("buy_value")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SummaryBuyOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    buy_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_ratio"),
            "chart_title": market_watch_chart_title_dict.get("buy_ratio")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class BuyOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    buy_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("buy_ratio"),
            "chart_title": market_watch_chart_title_dict.get("buy_ratio")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SummarySellOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    sell_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("sell_ratio"),
            "chart_title": market_watch_chart_title_dict.get("sell_ratio")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)


class SellOrderRatioSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    links = serializers.ListField()
    symbol = serializers.CharField()
    last_time = serializers.CharField()
    sell_ratio = RoundedFloatField(decimal_places=0)
    trade_count = serializers.IntegerField()
    volume = RoundedFloatField()
    value = RoundedFloatField()
    closing_price = RoundedFloatField()
    closing_price_change = RoundedFloatField(decimal_places=2)
    last_price = RoundedFloatField()
    last_price_change = RoundedFloatField(decimal_places=2)

    chart = serializers.DictField()

    def to_representation(self, instance):
        chart = {
            "x_title": MARKET_WATCH_X_TITLE,
            "y_title": market_watch_y_title_dict.get("sell_ratio"),
            "chart_title": market_watch_chart_title_dict.get("sell_ratio")
            + " "
            + instance["symbol"],
            "history": instance.get("history"),
        }

        instance["chart"] = chart
        instance["links"] = [
            {"name": "لینک تابلوی معاملات", "link": instance.get("link")}
        ]
        return super().to_representation(instance)
