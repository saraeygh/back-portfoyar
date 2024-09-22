from rest_framework import serializers


class RoundedFloatField(serializers.FloatField):
    def __init__(self, *args, **kwargs):
        self.decimal_places = kwargs.pop("decimal_places", 3)
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        rounded_value = round(value, self.decimal_places)
        return float(rounded_value)
