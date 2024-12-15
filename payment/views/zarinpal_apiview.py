import json
import requests
from datetime import datetime as dt, timedelta as td

from django.db import transaction as atomic_transaction
from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.configs import (
    ZARINPAL_MERCHANTID,
    ZARINPAL_VERIFY_TRANSACTION_CALLBACKURL,
    ZP_PAY_REQUEST_URL,
    ZP_STARTPAY_URL,
    ZP_REDIRECT_FRONTEND_URL,
    ZP_PAY_VERIFY_URL,
)
from payment.models import Receipt, ZARINPAL
from account.models import Feature, FeatureDiscount, UserDiscount, Subscription, Profile
from account.utils import is_valid_phone

OK_STATUS = 200
ZP_OK_STATUS_100 = "100"
ZP_OK_STATUS_101 = "101"
ZP_RES_STATUS = "zp-res-status-"
ZP_PAY_OK_STATUS = "OK"
REQUESTED_PAYMENT = "requested-payment"
PAY_REQ_STATUS = "pay-req-status-"
ZP_VERIFY_STATUS = "zp-verify-status-"
RECEIPT_CONFIRMED = "receipt-confirmed"
ZERO_PRICE_RECEIPT = "zero-price-receipt"

USER_DISCOUNT = UserDiscount.__name__
FEATURE_DISCOUNT = FeatureDiscount.__name__


def get_receipt_to_pay(user, receipt_id):
    receipt = Receipt.objects.filter(
        user=user, receipt_id=receipt_id, is_confirmed=False
    )
    if receipt.exists():
        return True, receipt.first()

    return False, Response(
        {"message": "شما مجاز به پرداخت تراکنشی با این شناسه نیستید"},
        status=status.HTTP_400_BAD_REQUEST,
    )


def get_receipt_to_confirm(receipt_id, pay_id):
    receipt = Receipt.objects.filter(
        receipt_id=receipt_id, pay_id=pay_id, is_confirmed=False
    )
    if receipt.exists():
        return True, receipt.first()

    return False, None


def update_receipt_desc(receipt: Receipt, updated_desc: str):
    receipt.description = updated_desc
    receipt.save()


def get_pay_request_response(data):
    data = json.dumps(data)
    headers = {
        "content-type": "application/json",
        "content-length": str(len(data)),
    }
    response = requests.post(
        ZP_PAY_REQUEST_URL,
        data=data,
        headers=headers,
        timeout=10,
    )

    return response


def check_pay_request_response(transaction, response):
    if response.status_code == OK_STATUS:
        update_receipt_desc(transaction, PAY_REQ_STATUS + str(OK_STATUS))

        response = response.json()
        response_status = str(response.get("Status"))
        authority = str(response.get("Authority"))

        if response_status != ZP_OK_STATUS_100:
            update_receipt_desc(transaction, ZP_RES_STATUS + response_status)

            errors = response.get("errors")
            return False, Response(errors, status=status.HTTP_400_BAD_REQUEST)

        update_receipt_desc(transaction, ZP_RES_STATUS + response_status)
        return True, authority

    else:
        update_receipt_desc(transaction, PAY_REQ_STATUS + str(response.status_code))
        return False, Response(
            {"message": f"درخواست نامعتبر ({response.status_code})"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def payment_info(data, receipt: Receipt):
    try:
        update_receipt_desc(receipt, REQUESTED_PAYMENT)
        response = get_pay_request_response(data)
        ok, result = check_pay_request_response(receipt, response)
        if not ok:
            return result
        authority = result
    except requests.exceptions.Timeout:
        update_receipt_desc(receipt, PAY_REQ_STATUS + "TIME-OUT")
        return Response(
            {
                "message": "مشکلی در ارتباط با درگاه پرداخت پیش آمده است (اتمام زمان انتظار)"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except requests.exceptions.ConnectionError:
        update_receipt_desc(receipt, PAY_REQ_STATUS + "CONN_ERROR")
        return Response(
            {"message": "مشکلی در ارتباط با درگاه پرداخت پیش آمده است (خطای اتصال)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    receipt.pay_id = authority
    receipt.save()

    pay_info = {
        "status": True,
        "authority": authority,
        "redirectUrl": ZP_STARTPAY_URL + authority,
    }

    return Response(data=pay_info, status=status.HTTP_200_OK)


def get_verify_pay_response(data):
    data = json.dumps(data)
    headers = {"content-type": "application/json", "content-length": str(len(data))}
    response = requests.post(ZP_PAY_VERIFY_URL, data=data, headers=headers, timeout=10)

    return response


def confirm_receipt(receipt: Receipt, tracking_id: str):
    receipt.is_confirmed = True
    receipt.tracking_id = tracking_id
    receipt.description = RECEIPT_CONFIRMED
    receipt.save()


def update_profile_max_login(user, plan: Feature):
    profile: Profile = user.profile
    profile.max_login = plan.login_count
    profile.save()


def create_update_subscription(user, plan: Feature):
    current_date = dt.now().date()
    current_sub = Subscription.objects.filter(
        is_enabled=True, user=user, feature__name=plan.name, end_at__gte=current_date
    ).first()

    if current_sub is None:
        end_date = current_date + td(days=plan.duration * 30)
        Subscription.objects.create(
            user=user, feature=plan, start_at=current_date, end_at=end_date
        )
        return

    current_sub.end_at = current_sub.end_at + td(days=plan.duration * 30)
    current_sub.save()


def update_discount(discount: FeatureDiscount | UserDiscount):
    if discount.has_max_use_count:
        discount.used_count += 1
        discount.save()


def finalize_buying_subscription(receipt: Receipt, tracking_id):
    user = receipt.user
    plan = receipt.feature
    discount = receipt.discount_object
    with atomic_transaction.atomic():
        confirm_receipt(receipt, tracking_id)
        update_profile_max_login(user, plan)
        create_update_subscription(user, plan)
        if discount:
            update_discount(discount)


class ZarinpalPaymentAPIView(APIView):
    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return [TokenAuthentication()]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request, receipt_id):
        user = request.user
        receipt_exists, result = get_receipt_to_pay(user, receipt_id)
        if not receipt_exists:
            return result

        receipt = result
        receipt.method = ZARINPAL
        receipt.save()
        if receipt.price == 0:
            FRONT_REDIRECT_URL = (
                f"{request.scheme}://{request.get_host()}" + ZP_REDIRECT_FRONTEND_URL
            )
            finalize_buying_subscription(receipt, ZERO_PRICE_RECEIPT)
            return redirect(FRONT_REDIRECT_URL)

        data = {
            "MerchantID": ZARINPAL_MERCHANTID,
            "Amount": receipt.price,
            "Description": "اشتراک سامانه پرتفویار",
            "CallbackURL": f"{request.scheme}://{request.get_host()}"
            + ZARINPAL_VERIFY_TRANSACTION_CALLBACKURL
            + receipt_id
            + "/",
        }

        if is_valid_phone(user.username):
            data["Phone"] = user.username

        return payment_info(data, receipt)

    def get(self, request, receipt_id):
        authority = request.query_params.get("Authority", None)
        receipt_exists, receipt = get_receipt_to_confirm(receipt_id, authority)

        FRONT_REDIRECT_URL = (
            f"{request.scheme}://{request.get_host()}" + ZP_REDIRECT_FRONTEND_URL
        )
        if not receipt_exists:
            return redirect(FRONT_REDIRECT_URL)

        query_status = request.query_params.get("Status", None)
        if query_status != ZP_PAY_OK_STATUS:
            update_receipt_desc(receipt, ZP_VERIFY_STATUS + query_status)
            return redirect(FRONT_REDIRECT_URL)
        update_receipt_desc(receipt, ZP_VERIFY_STATUS + query_status)

        data = {
            "MerchantID": ZARINPAL_MERCHANTID,
            "Amount": receipt.price,
            "Authority": receipt.pay_id,
        }

        response = get_verify_pay_response(data)
        if response.status_code != OK_STATUS:
            update_receipt_desc(receipt, ZP_VERIFY_STATUS + str(response.status_code))
            return redirect(FRONT_REDIRECT_URL)

        response = response.json()
        response_status = str(response.get("Status"))
        tracking_id = str(response.get("RefID"))
        if response_status not in [ZP_OK_STATUS_100, ZP_OK_STATUS_101]:
            update_receipt_desc(
                receipt,
                ZP_VERIFY_STATUS
                + "Status-"
                + response_status
                + "-tracking_id-"
                + tracking_id,
            )
            return redirect(FRONT_REDIRECT_URL)

        finalize_buying_subscription(receipt, tracking_id)

        return redirect(FRONT_REDIRECT_URL)
