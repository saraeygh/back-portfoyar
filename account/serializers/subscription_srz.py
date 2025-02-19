from rest_framework import serializers

from account.models import Subscription


class GetSubscriptionSerailizer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = [
            "id",
            "feature_name",
            "is_active",
            "remained_days",
            "total_days",
            "start_at_shamsi",
            "end_at_shamsi",
        ]
