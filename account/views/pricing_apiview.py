from uuid import uuid4
from datetime import datetime as dt
import pytz

import jdatetime

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token

from core.configs import TEHRAN_TZ
from payment.models import Receipt
from account.models import (
    Feature,
    FeatureDiscount,
    UserDiscount,
    FEATURE_DURATION_CHOICES,
    SUBSCRIPTION_FEATURE_CHOICES,
)

DURATIONS = {duration[0]: duration[1] for duration in FEATURE_DURATION_CHOICES}
FEATURES = {feature[0]: feature[1] for feature in SUBSCRIPTION_FEATURE_CHOICES}


def get_request_user(request):
    try:
        auth_header = get_authorization_header(request).decode("utf-8")
        token_key = auth_header.split(" ")[1]
        token = Token.objects.get(key=token_key)
        request.user = token.user
    except Exception:
        request.user = AnonymousUser()

    return request


def get_best_user_discount(plan, user):
    return (
        plan.user_discounts.filter(is_enabled=True, feature=plan, user=user)
        .order_by("-discount_percent")
        .first()
    )


def get_best_feature_discount(plan):
    return (
        plan.discounts.filter(is_enabled=True, feature=plan)
        .order_by("-discount_percent")
        .first()
    )


def get_discount_info(plan, discount: FeatureDiscount | UserDiscount):
    discount_info = {
        "id": plan.id,
        "name": discount.name,
        "description": discount.description,
        "discount_percent": discount.discount_percent,
        "has_discount_code": discount.has_discount_code,
        "has_start": discount.has_start,
        "start_date": jdatetime.datetime.fromgregorian(
            datetime=discount.start_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d"),
        "start_time": jdatetime.datetime.fromgregorian(
            datetime=discount.start_at, tzinfo=TEHRAN_TZ
        ).strftime("%H:%M:%S"),
        "has_expiry": discount.has_expiry,
        "expiry_date": jdatetime.datetime.fromgregorian(
            datetime=discount.expire_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d"),
        "expiry_time": jdatetime.datetime.fromgregorian(
            datetime=discount.expire_at, tzinfo=TEHRAN_TZ
        ).strftime("%H:%M:%S"),
        "has_max_use_count": discount.has_max_use_count,
        "used_count": discount.used_count,
        "max_use_count": discount.max_use_count,
    }

    return discount_info


def get_best_discount(plan, user):
    if user.is_authenticated:
        user_discount = get_best_user_discount(plan, user)
    else:
        user_discount = None

    feature_discount = get_best_feature_discount(plan)

    if user_discount:
        discount = user_discount
    elif feature_discount:
        discount = feature_discount
    else:
        discount = None

    return discount


def get_plan_discount(plan, user):
    discount = get_best_discount(plan, user)
    if discount:
        discount = get_discount_info(plan, discount)

    return discount


def get_all_plans(user):
    features = list(
        Feature.objects.filter(is_enabled=True)
        .distinct("name")
        .values_list("name", flat=True)
    )
    all_plans = {}
    for feature in features:
        all_plans[feature] = {"name": FEATURES.get(feature), "plans": []}

        feature_plans = Feature.objects.filter(name=feature, is_enabled=True).order_by(
            "price"
        )
        for feature_plan in feature_plans:
            discount = get_plan_discount(feature_plan, user)
            discount = {} if discount is None else discount

            all_plans[feature]["plans"].append(
                {
                    "id": feature_plan.id,
                    "duration": DURATIONS.get(feature_plan.duration),
                    "price": feature_plan.price,
                    "has_discount": feature_plan.has_discount,
                    "discount_percent": feature_plan.discount_percent,
                    "discounted_price": feature_plan.discounted_price,
                    "login_count": feature_plan.login_count,
                    "discount": discount,
                }
            )

    return all_plans


def add_discount(receipt, discount: FeatureDiscount | UserDiscount, user_code: str):
    if discount is None:
        return receipt
    receipt["discount_type"] = ContentType.objects.get_for_model(type(discount))
    receipt["discount_id"] = discount.id
    receipt["discount_object"] = discount

    return receipt


def calculated_final_price(plan, price, discount, user, code):
    receipt = {}
    receipt["user"] = user
    receipt["feature"] = plan

    has_special_discount = False
    receipt = add_discount(receipt, discount, code)
    if "discount_type" in receipt:
        has_special_discount = True

    receipt["receipt_id"] = uuid4().hex
    receipt["price"] = price
    new_receipt = Receipt(**receipt)
    new_receipt.save()

    final_price = {
        "name": FEATURES.get(plan.name),
        "duration": plan.duration,
        "login_count": plan.login_count,
        "price": price,
        "receipt_id": new_receipt.receipt_id,
        "has_special_discount": has_special_discount,
    }

    return Response(final_price, status=status.HTTP_200_OK)


def apply_discount(plan, discount, code, user):
    now = dt.now(tz=pytz.UTC)
    if discount.has_start and discount.start_at > now:
        return Response(
            {"message": f"زمان استفاده از طرح {discount.name} فرا نرسیده است"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if discount.has_max_use_count and discount.used_count >= discount.max_use_count:
        return Response(
            {
                "message": f"محدودیت تعداد دفعات استفاده از طرح {discount.name} به پایان رسیده است"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if discount.has_expiry and discount.expire_at < now:
        return Response(
            {"message": f"زمان استفاده از طرح {discount.name} به پایان رسیده است"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if (
        discount.has_discount_code
        and code != ""
        and discount.discount_code.lower() != code.lower()
    ):
        return Response(
            {"message": "کد تخفیف وارد شده اشتباه است"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    plan_price = plan.discounted_price
    price = int(plan_price * (1 - (discount.discount_percent / 100)))

    return calculated_final_price(plan, price, discount, user, code)


def get_final_price(plan, user, code):
    discount = get_best_discount(plan, user)

    if discount:
        return apply_discount(plan, discount, code, user)
    else:
        return calculated_final_price(plan, plan.discounted_price, discount, user, code)


class PricingAPIView(APIView):

    def get(self, request):
        request = get_request_user(request)

        plans = get_all_plans(request.user)
        return Response(plans, status=status.HTTP_200_OK)

    def post(self, request):
        request = get_request_user(request)

        code = str(request.data.get("code", ""))
        plan_id = int(request.data.get("plan_id", 0))
        plan = get_object_or_404(Feature, id=plan_id)

        return get_final_price(plan, request.user, code)
