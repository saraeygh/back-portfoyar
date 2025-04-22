import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime
from django.contrib import admin
from support.models import Ticket, TicketResponse


class TicketResponseInline(admin.StackedInline):
    model = TicketResponse
    fields = ("user", "text", "file")
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    autocomplete_fields = ("sender_user", "receiver_user")
    list_display = (
        "id",
        "sender_user",
        "receiver_user",
        "unit",
        "feature",
        "title",
        "status",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "title")
    ordering = ("-updated_at",)

    search_fields = ("id", "title", "sender_user__username", "receiver_user__username")

    list_filter = ("status", "feature", "unit")
    inlines = (TicketResponseInline,)

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: Ticket):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: Ticket):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    autocomplete_fields = ("ticket", "user")
    list_display = ("id", "ticket", "user", "created_at_shamsi", "updated_at_shamsi")

    list_display_links = ("id", "ticket")
    ordering = ("-updated_at",)

    search_fields = ("id", "ticket__title", "text", "user__username")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: TicketResponse):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: TicketResponse):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
