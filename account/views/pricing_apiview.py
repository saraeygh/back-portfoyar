import jdatetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import TEHRAN_TZ
from account.models import Feature, FEATURE_DURATION_CHOICES

DURATIONS = {duration[0]: duration[1] for duration in FEATURE_DURATION_CHOICES}


def get_all_plans():
    features = list(Feature.objects.distinct("name").values_list("name", flat=True))
    plans = {}
    for feature in features:
        plans[feature] = []

        feature_plans = Feature.objects.filter(name=feature).order_by("price")
        for feature_plan in feature_plans:
            new_plan = {
                "id": feature_plan.id,
                "duration": DURATIONS.get(feature_plan.duration),
                "price": feature_plan.price,
                "has_discount": feature_plan.has_discount,
                "discount_percent": feature_plan.discount_percent,
                "discounted_price": feature_plan.discounted_price,
                "login_count": feature_plan.login_count,
                "discounts": [],
            }

            discounts = feature_plan.discounts.all()
            if discounts.exists():
                for discount in discounts:
                    if discount.is_enabled:
                        new_discount = {
                            "name": discount.name,
                            "description": discount.description,
                            #
                            "discount_percent": discount.discount_percent,
                            "has_discount_code": discount.has_discount_code,
                            #
                            "has_start": discount.has_start,
                            "start_at": jdatetime.datetime.fromgregorian(
                                datetime=discount.start_at, tzinfo=TEHRAN_TZ
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            #
                            "has_expiry": discount.has_expiry,
                            "expire_at": jdatetime.datetime.fromgregorian(
                                datetime=discount.expire_at, tzinfo=TEHRAN_TZ
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            #
                            "has_max_use_count": discount.has_max_use_count,
                            "max_use_count": discount.max_use_count,
                            "used_count": discount.used_count,
                        }
                        new_plan["discounts"].append(new_discount)

            plans[feature].append(new_plan)

    return plans


class PricingAPIView(APIView):
    def get(self, request):
        plans = get_all_plans()
        return Response(plans, status=status.HTTP_200_OK)
