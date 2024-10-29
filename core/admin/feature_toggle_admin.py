import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from core.models import FeatureToggle


@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "state",
        "value",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "name")

    ordering = ("-updated_at",)

    search_fields = ("name", "desc", "value")

    readonly_fields = ("name", "created_at", "updated_at")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: FeatureToggle):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: FeatureToggle):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
