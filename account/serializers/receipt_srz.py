from rest_framework import serializers

from payment.models import Receipt


class GetReceiptSerailizer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = [
            "id",
            #
            "feature_name",
            "feature_duration",
            "feature_login_count",
            "feature_price",
            "feature_discount",
            #
            "discount_name",
            "discount_percent",
            #
            "price",
            "method_name",
            #
            "is_confirmed",
            "tracking_id",
        ]
