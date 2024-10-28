import jdatetime
import json
import pytz
import os
from persiantools.jdatetime import JalaliDateTime
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from collections import OrderedDict
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from support.models import Ticket, FEATURE_CHOICES, UNIT_CHOICES, OPEN
from support.serializers import (
    GetUserTicketsSerailizer,
    AddUserTicketsSerailizer,
    GetTicketResponseSerailizer,
    AddTicketResponseSerailizer,
)
from django.http import HttpResponse

from . import TICKET_APPENDIX_FILES_DIR
from colorama import Fore, Style

FILE_SIZE_LIMIT = 10_000_000


def get_user_tickets(request):
    user = request.user
    user_tickets = Ticket.objects.filter(
        Q(sender_user=user) | Q(receiver_user=user)
    ).order_by("-updated_at")
    user_tickets = GetUserTicketsSerailizer(
        user_tickets, many=True, context={"request": request}
    )

    return Response(user_tickets.data, status=status.HTTP_200_OK)


def create_dir_if_not_exists():
    is_dir = os.path.isdir(TICKET_APPENDIX_FILES_DIR)
    if not is_dir:
        os.makedirs(TICKET_APPENDIX_FILES_DIR)


def decrease_filename_lenght(filename: str):
    if len(filename) > 255:
        diff_idx = len(filename) - 255 + 1
        filename = filename[diff_idx:]

    return filename


def save_appendix_file(file):

    file_size = file.size
    if file_size > FILE_SIZE_LIMIT:
        return Response(
            {"message": "حجم فایل نباید بیشتر از ۱۰ مگابایت باشد."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    create_dir_if_not_exists()

    original_filename = file.name
    original_filename = original_filename.replace(" ", "-")
    original_filename = original_filename.replace("/", "-")
    new_filename = decrease_filename_lenght(original_filename)

    file.name = new_filename
    FILE_PATH = TICKET_APPENDIX_FILES_DIR + new_filename
    result = default_storage.save(FILE_PATH, file)
    saved_filename = result.split("/")[1]

    return saved_filename


def add_ticket_as_first_response(request, ticket, responses):
    created_at = JalaliDateTime(
        ticket.created_at, tzinfo=pytz.UTC
    ) + jdatetime.timedelta(hours=3, minutes=30)

    first_response = {
        "id": ticket.id,
        "text": ticket.text,
        "date": jdatetime.datetime.fromgregorian(datetime=created_at).strftime(
            format="%Y/%m/%d"
        ),
        "time": jdatetime.datetime.fromgregorian(datetime=created_at).strftime(
            format="%H:%M"
        ),
        "user": ticket.sender_user.get_full_name(),
        "is_staff": ticket.sender_user.is_staff,
        "appendix": None,
    }
    if ticket.file:
        file_url = (
            f"{request.build_absolute_uri("/api/support/appendix/")}{ticket.file}/"
        )
        first_response["appendix"] = file_url
    first_response = OrderedDict(sorted(first_response.items()))

    responses = list(responses.data)
    responses.insert(0, first_response)

    return responses


def get_ticket_detail(request, ticket_id):
    ticket_obj = get_object_or_404(Ticket, id=ticket_id)

    ticket = GetUserTicketsSerailizer(ticket_obj, context={"request": request})
    ticket = ticket.data

    responses = ticket_obj.responses.order_by("updated_at")
    responses = GetTicketResponseSerailizer(
        responses, many=True, context={"request": request}
    )

    ticket["responses"] = add_ticket_as_first_response(request, ticket_obj, responses)

    return Response(ticket, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetTicketUnitListAPIView(APIView):
    def get(self, request):
        units = list()
        for unit in UNIT_CHOICES:
            units.append({"id": unit[0], "name": unit[1]})

        return Response(units, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetTicketFeatureListAPIView(APIView):
    def get(self, request):
        features = list()
        for feature in FEATURE_CHOICES:
            features.append({"id": feature[0], "name": feature[1]})

        return Response(features, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TicketingAPIView(APIView):
    def get(self, request):
        return get_user_tickets(request=request)

    def post(self, request):

        try:
            ticket = json.loads(request.data.get("ticket"))
        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
            return Response(
                {"message": "مشکلی پیش آمده است."}, status=status.HTTP_400_BAD_REQUEST
            )

        new_ticket = {
            "sender_user": request.user.id,
            "receiver_user": User.objects.filter(username="admin").first().id,
            "unit": ticket.get("unit"),
            "feature": ticket.get("feature"),
            "title": ticket.get("title"),
            "text": ticket.get("text"),
        }

        file = request.FILES.get("appendix")
        if file:
            new_ticket["file"] = save_appendix_file(file=file)

        new_ticket_srz = AddUserTicketsSerailizer(data=new_ticket)
        new_ticket_srz.is_valid(raise_exception=True)
        ticket = new_ticket_srz.save()

        return get_ticket_detail(request=request, ticket_id=ticket.id)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetTicketDetailAPIView(APIView):
    def get(self, request, ticket_id):
        return get_ticket_detail(request=request, ticket_id=ticket_id)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        try:
            response = json.loads(request.data.get("response"))
        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
            return Response(
                {"message": "مشکلی پیش آمده است."}, status=status.HTTP_400_BAD_REQUEST
            )

        new_response = {
            "ticket": ticket.id,
            "user": request.user.id,
            "text": response.get("text"),
        }

        file = request.FILES.get("appendix")
        if file:
            new_response["file"] = save_appendix_file(file=file)

        new_response_srz = AddTicketResponseSerailizer(data=new_response)
        new_response_srz.is_valid(raise_exception=True)
        new_response = new_response_srz.save()

        ticket.updated_at = new_response.updated_at
        ticket.status = OPEN
        ticket.save()

        return get_ticket_detail(request=request, ticket_id=ticket_id)


class DisableAnonThrottle(AnonRateThrottle):
    def allow_request(self, request, view):
        if request.user.is_anonymous and isinstance(view, GetTicketAppendixAPIView):
            return True
        return super().allow_request(request, view)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
class GetTicketAppendixAPIView(APIView):
    throttle_classes = [DisableAnonThrottle]

    def get(self, request, file_name):
        file_path = f"{TICKET_APPENDIX_FILES_DIR}{file_name}"

        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
            response = HttpResponse(file_data, content_type="application/octet-stream")
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            print(Fore.RED)
            print(e)
            print(Style.RESET_ALL)
            return Response(
                {"message": "فایل پیدا نشد."}, status=status.HTTP_404_NOT_FOUND
            )
