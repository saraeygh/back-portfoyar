import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from django.http.request import HttpRequest
from domestic_market.models import DomesticTradesHistoryFetch


@admin.register(DomesticTradesHistoryFetch)
class DomesticTradesHistoryFetchAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest):
        return False

    list_display = (
        "id",
        "start_date",
        "end_date",
        "request_sent",
        "received_trades",
        "start_populating_db",
        "db_populated",
        "number_of_trades_received",
        "number_of_populated_trades",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "start_date",
        "end_date",
        "request_sent",
        "received_trades",
        "start_populating_db",
        "db_populated",
        "number_of_trades_received",
        "number_of_populated_trades",
    )

    ordering = ("-updated_at",)

    search_fields = (
        "id",
        "start_date",
        "end_date",
        "request_sent",
        "received_trades",
        "start_populating_db",
        "db_populated",
        "number_of_trades_received",
        "number_of_populated_trades",
    )

    readonly_fields = (
        "id",
        "start_date",
        "end_date",
        "request_sent",
        "received_trades",
        "start_populating_db",
        "db_populated",
        "number_of_trades_received",
        "number_of_populated_trades",
        "created_at",
        "updated_at",
    )

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticTradesHistoryFetch):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticTradesHistoryFetch):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
