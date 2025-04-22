from rest_framework import serializers
import jdatetime as jdt

from payment.models import Receipt
from core.configs import TEHRAN_TZ


class GetReceiptSerailizer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = [
            "id",
            #
            "feature_name",
            "feature_duration",
            "feature_login_count",
            # "feature_price",
            # "feature_discount",
            #
            "discount_name",
            "discount_percent",
            #
            "price",
            "method_name",
            #
            "is_confirmed",
            "tracking_id",
            "updated_at",
        ]

    def to_representation(self, instance):
        shamsi = (
            jdt.datetime.fromgregorian(datetime=instance.updated_at, tzinfo=TEHRAN_TZ)
            + jdt.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        representation = super().to_representation(instance)
        representation["updated_at"] = shamsi

        return representation
