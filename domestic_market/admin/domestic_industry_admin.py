import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from domestic_market.models import DomesticIndustry


@admin.register(DomesticIndustry)
class DomesticIndustryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "created_at_shamsi", "updated_at_shamsi")

    list_display_links = ("id", "name", "code")

    ordering = ("-updated_at",)

    search_fields = ("name", "code")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticIndustry):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticIndustry):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
