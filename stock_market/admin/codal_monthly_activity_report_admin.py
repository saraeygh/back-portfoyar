import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from stock_market.models import CodalMonthlyActivityReport


@admin.register(CodalMonthlyActivityReport)
class StockMonthlyActivityReportAdmin(admin.ModelAdmin):
    autocomplete_fields = ("company",)
    list_display = (
        "id",
        "tracing_number",
        "company",
        "title",
        "publish_date_time_shamsi",
        "has_html",
        "has_excel",
        "has_pdf",
        "has_xbrl",
        "has_attachment",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "id",
        "tracing_number",
        "company",
        "title",
    )

    list_filter = (
        "has_html",
        "has_excel",
        "has_pdf",
        "has_xbrl",
        "has_attachment",
    )

    ordering = ("-updated_at",)

    search_fields = (
        "id",
        "tracing_number",
        "company__symbol",
        "company__name",
        "title",
    )

    @admin.display(description="زمان انتشار شمسی")
    def publish_date_time_shamsi(self, obj: CodalMonthlyActivityReport):
        shamsi = (JalaliDateTime(obj.publish_date_time, tzinfo=pytz.UTC)).strftime(
            "%Y/%m/%d %H:%M:%S"
        )

        return shamsi

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: CodalMonthlyActivityReport):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: CodalMonthlyActivityReport):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
