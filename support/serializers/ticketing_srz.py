from datetime import datetime
import pytz
from rest_framework import serializers
from support.models import Ticket, TicketResponse, FEATURE_CHOICES, STATUS_CHOICES, UNIT_CHOICES
import jdatetime

FEATURES = {feature[0]: feature[1] for feature in FEATURE_CHOICES}
STATUSES = {status[0]: status[1] for status in STATUS_CHOICES}
UNITS = {unit[0]: unit[1] for unit in UNIT_CHOICES}


def get_last_update(last_update):

    last_update = last_update.replace(tzinfo=pytz.UTC)
    now = datetime.now(pytz.UTC)

    diff = now - last_update
    seconds = int(diff.total_seconds())
    minutes = int(seconds / 60)
    hours = int(seconds / (60 * 60))
    days = int(seconds / (60 * 60 * 24))
    months = int(seconds / (60 * 60 * 24 * 30))
    years = int(seconds / (60 * 60 * 24 * 30 * 12))

    if years > 0:
        return f"{years} سال پیش"
    elif months > 0:
        return f"{months} ماه پیش"
    elif days > 0:
        return f"{days} روز پیش"
    elif hours > 0:
        return f"{hours} ساعت پیش"
    elif minutes > 0:
        return f"{minutes} دقیقه پیش"
    else:
        return f"{seconds} ثانیه پیش"


class GetUserTicketsSerailizer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    def get_sender_name(self, instance):
        sender_name = instance.sender_user.get_full_name()
        return sender_name

    def get_receiver_name(self, instance):
        try:
            receiver_name = instance.receiver_user.get_full_name()
            return receiver_name
        except Exception:
            return "ادمین سایت"

    def to_representation(self, instance):
        responses = instance.responses

        if responses.count() > 0:
            last_update = responses.order_by("-updated_at").first()
            last_update = last_update.updated_at
        else:
            last_update = instance.updated_at

        representation = super().to_representation(instance)
        representation["response_count"] = responses.count()
        representation["last_update"] = get_last_update(last_update)
        if instance.file:
            request = self.context.get("request")
            file_url = f"{request.build_absolute_uri("/api/support/appendix/")}{instance.file}/"
            representation["appendix"] = file_url
        else:
            representation["appendix"] = None

        representation["feature"] = FEATURES.get(representation["feature"])
        representation["status"] = STATUSES.get(representation["status"])
        representation["unit"] = UNITS.get(representation["unit"])

        representation["sender"] = representation.pop("sender_name")
        representation["receiver"] = representation.pop("receiver_name")

        return representation

    class Meta:
        model = Ticket
        fields = ["id", "sender_name", "receiver_name", "unit", "feature", "title", "status"]


class AddUserTicketsSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["sender_user", "receiver_user", "unit", "feature", "title", "text", "file"]


class GetTicketResponseSerailizer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, instance):
        user_name = instance.user.get_full_name()
        return user_name

    class Meta:
        model = TicketResponse
        fields = ["id", "user_name", "text"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        updated_at = instance.updated_at
        updated_at = jdatetime.datetime.fromgregorian(datetime=updated_at).strftime(format="%Y-%m-%d - %H:%m")
        representation["last_update"] = updated_at

        if instance.file:
            request = self.context.get("request")
            file_url = f"{request.build_absolute_uri("/api/support/appendix/")}{instance.file}/"
            representation["appendix"] = file_url
        else:
            representation["appendix"] = None

        representation["user"] = representation.pop("user_name")
        representation["is_staff"] = instance.user.is_staff

        return representation


class AddTicketResponseSerailizer(serializers.ModelSerializer):
    class Meta:
        model = TicketResponse
        fields = ["ticket", "user", "text", "file"]
