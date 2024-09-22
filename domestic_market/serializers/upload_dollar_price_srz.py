import re

import jdatetime
from rest_framework import serializers


class UploadDollarPriceSerializer(serializers.Serializer):
    date = serializers.CharField()
    nima = serializers.IntegerField()
    azad = serializers.IntegerField()

    DATE_PATTERN = r"1(2\d\d|3\d\d|4\d\d)-(0\d|1[0-2])-(0\d|1\d|2\d|3[0-1])"

    def validate_date(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("تاریخ نامعتبر")

        match = re.search(self.DATE_PATTERN, value)
        if match:
            date = match.group(0)
            year, month, day = date.split("-")

            value = jdatetime.date(
                year=int(year),
                month=int(month),
                day=int(day),
            ).togregorian()

        else:
            raise serializers.ValidationError("تاریخ نامعتبر")

        return value

    def validate_nima(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("قیمت نیمایی نامعتبر")

        return value

    def validate_azad(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("قیمت آزاد نامعتبر")

        return value
