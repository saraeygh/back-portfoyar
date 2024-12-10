from uuid import uuid4
import pytz
import jdatetime
from datetime import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import TEHRAN_TZ
from payment.models import Transaction
from account.models import (
    Feature,
    FeatureDiscount,
    UserDiscount,
    FEATURE_DURATION_CHOICES,
    SUBSCRIPTION_FEATURE_CHOICES,
)

DURATIONS = {duration[0]: duration[1] for duration in FEATURE_DURATION_CHOICES}
FEATURES = {feature[0]: feature[1] for feature in SUBSCRIPTION_FEATURE_CHOICES}


def get_all_plans():
    features = list(Feature.objects.distinct("name").values_list("name", flat=True))
    all_plans = {}
    for feature in features:
        all_plans[feature] = {"name": FEATURES.get(feature), "plans": []}

        feature_plans = Feature.objects.filter(name=feature).order_by("price")
        for feature_plan in feature_plans:
            all_plans[feature]["plans"].append(
                {
                    "id": feature_plan.id,
                    "duration": DURATIONS.get(feature_plan.duration),
                    "price": feature_plan.price,
                    "has_discount": feature_plan.has_discount,
                    "discount_percent": feature_plan.discount_percent,
                    "discounted_price": feature_plan.discounted_price,
                    "login_count": feature_plan.login_count,
                }
            )

    return all_plans


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


def get_discount_info(plan, discount):
    discount = {
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

    return discount


def get_best_discount(plan, user):
    user_discount = get_best_user_discount(plan, user)
    feature_discount = get_best_feature_discount(plan)

    if user_discount:
        discount = user_discount
    elif feature_discount:
        discount = feature_discount
    else:
        discount = {}

    return discount


def get_plan_discount(plan, user):
    discount = get_best_discount(plan, user)
    if discount:
        discount = get_discount_info(plan, discount)

    return discount


def get_plan_str(plan: Feature):
    feat = f"feat: {plan.name},"
    dur = f"dur: {plan.duration},"
    login = f"login: {plan.login_count},"
    pr = f"pr: {plan.price},"
    dis_per = "dis_per: ...,"
    dis_pr = "dis_pr: ..."
    if plan.has_discount:
        dis_per = f"dis_per: {plan.discount_percent},"
        dis_pr = f"dis_pr: {plan.discounted_price}"

    return " ".join([feat, dur, login, pr, dis_per, dis_pr])


def get_discount_str(discount: FeatureDiscount | UserDiscount, user_code: str):
    if not discount:
        return

    tp = f"tp: {discount.__class__.__name__},"
    name = f"name: {discount.name},"
    dis_per = f"dis_per: {discount.discount_percent},"

    code = "code: ... | ...,"
    if discount.has_discount_code:
        code = f"code: {user_code} | {discount.discount_code},"

    st = "st: ...,"
    if discount.has_start:
        st = f"st: {jdatetime.datetime.fromgregorian(datetime=discount.start_at, tzinfo=TEHRAN_TZ).strftime("%Y-%m-%d %H:%M:%S")},"

    ex = "ex: ...,"
    if discount.has_expiry:
        ex = f"ex: {jdatetime.datetime.fromgregorian(datetime=discount.expire_at, tzinfo=TEHRAN_TZ).strftime("%Y-%m-%d %H:%M:%S")},"

    use = "use: False | ... | ..."
    if discount.has_max_use_count:
        use = f"use: True | {discount.used_count} | {discount.max_use_count}"

    return " ".join([tp, name, dis_per, code, st, ex, use])


def calculated_final_price(plan, price, discount, user, code):
    transaction = {}
    transaction["user"] = user
    transaction["tx_id"] = uuid4().hex
    transaction["plan"] = get_plan_str(plan)
    transaction["discount"] = get_discount_str(discount, code)
    transaction["price"] = price
    new_tx = Transaction(**transaction)
    new_tx.save()

    final_price = {
        "id": plan.id,
        "name": FEATURES.get(plan.name),
        "duration": plan.duration,
        "login_count": plan.login_count,
        "price": price,
        "tx_id": new_tx.tx_id,
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


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PlansAPIView(APIView):
    def get(self, request):
        plans = get_all_plans()
        return Response(plans, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PlanAPIView(APIView):
    def get(self, request, plan_id):
        user = request.user
        plan = get_object_or_404(Feature, id=plan_id)
        discount = get_plan_discount(plan, user)

        return Response(discount, status=status.HTTP_200_OK)

    def post(self, request, plan_id):
        user = request.user
        code = request.data.get("code", "")
        plan = get_object_or_404(Feature, id=plan_id)

        return get_final_price(plan, user, code)
