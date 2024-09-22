from rest_framework import serializers


class GlobalTradeSerializer(serializers.Serializer):
    industry = serializers.CharField()
    commodity_type = serializers.CharField()
    commodity = serializers.CharField()
    transit = serializers.CharField()
    unit = serializers.CharField()
    trades = serializers.DictField()

    def validate_industry(self, industry_name):
        if industry_name is None or industry_name == "":
            raise serializers.ValidationError("صنعت نامعتبر")
        else:
            return str(industry_name)

    def validate_commodity_type(self, commodity_type_name):
        if commodity_type_name is None or commodity_type_name == "":
            raise serializers.ValidationError("نوع کالا نامعتبر")
        else:
            return str(commodity_type_name)

    def validate_commodity(self, commodity_name):
        if commodity_name is None or commodity_name == "":
            raise serializers.ValidationError("کالا نامعتبر")
        else:
            return str(commodity_name)

    def validate_transit(self, transit_name):
        if transit_name is None or transit_name == "":
            raise serializers.ValidationError("حمل و نقل نامعتبر")
        else:
            return str(transit_name)

    def validate_unit(self, unit_name):
        if unit_name is None or unit_name == "":
            raise serializers.ValidationError("واحد نامعتبر")
        else:
            return str(unit_name)

    def validate_trades(self, trades_dict: dict):
        new_trades_dict = trades_dict.copy()

        for trade_date, price in trades_dict.items():
            if price is None or not isinstance(price, float) or str(price) == "nan":
                new_trades_dict.pop(trade_date)

        return new_trades_dict
