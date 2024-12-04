from datetime import datetime
import pytz
from rest_framework import serializers
from support.models import (
    Ticket,
    TicketResponse,
    FEATURE_CHOICES,
    STATUS_CHOICES,
    UNIT_CHOICES,
)
import jdatetime
from persiantools.jdatetime import JalaliDateTime

FEATURES = {feature[0]: feature[1] for feature in FEATURE_CHOICES}
STATUSES = {status[0]: status[1] for status in STATUS_CHOICES}
UNITS = {unit[0]: unit[1] for unit in UNIT_CHOICES}


def get_short_text(text: str, max_word_count: int = 10):
    text = text.split(" ")
    THREE_DOTS = ""
    if len(text) > max_word_count:
        text = text[:max_word_count]
        THREE_DOTS = " ..."

    text = " ".join(text) + THREE_DOTS
    return text


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

    def to_representation(self, instance: Ticket):
        representation = super().to_representation(instance)

        representation["response_count"] = instance.responses.count()
        representation["last_update"] = get_last_update(instance.updated_at)

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

        last_response = instance.responses.last()
        if last_response:
            representation["text"] = get_short_text(last_response.text)
        else:
            representation["text"] = get_short_text(instance.text)

        return representation

    class Meta:
        model = Ticket
        fields = [
            "id",
            "sender_name",
            "receiver_name",
            "unit",
            "feature",
            "title",
            "status",
        ]


class AddUserTicketsSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "sender_user",
            "receiver_user",
            "unit",
            "feature",
            "title",
            "text",
            "file",
        ]


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

        updated_at = JalaliDateTime(
            instance.updated_at, tzinfo=pytz.UTC
        ) + jdatetime.timedelta(hours=3, minutes=30)

        representation["date"] = updated_at.strftime("%Y/%m/%d")
        representation["time"] = updated_at.strftime("%H:%M")

        representation["user"] = representation.pop("user_name")
        representation["is_staff"] = instance.user.is_staff

        if instance.file:
            request = self.context.get("request")
            file_url = f"{request.build_absolute_uri("/api/support/appendix/")}{instance.file}/"
            representation["appendix"] = file_url
        else:
            representation["appendix"] = None

        return representation


class AddTicketResponseSerailizer(serializers.ModelSerializer):
    class Meta:
        model = TicketResponse
        fields = ["ticket", "user", "text", "file"]
