import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from typing import Any
from django.contrib import admin
from domestic_market.models import BourseViewCookie
from domestic_market.utils import get_dollar_price_history


@admin.register(BourseViewCookie)
class BourseViewCookieAdmin(admin.ModelAdmin):
    list_display = ("id", "cookie", "created_at_shamsi", "updated_at_shamsi")

    list_display_links = ("id", "cookie")

    ordering = ("-updated_at",)

    search_fields = ("cookie",)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)
        get_dollar_price_history()
        return super().save_model(request, obj, form, change)

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: BourseViewCookie):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: BourseViewCookie):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
