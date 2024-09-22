import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from global_market.models import GlobalCommodityType


@admin.register(GlobalCommodityType)
class GlobalCommodityTypeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("industry",)
    list_display = (
        "id",
        "industry",
        "name",
        "created_at_shamsi",
        "updated_at_shamsi",
        "id_industry",
    )

    list_display_links = ("id", "industry", "name")

    ordering = ("-updated_at",)

    search_fields = ("industry__name", "name")

    @admin.display(description="صنعت id")
    def id_industry(self, obj):
        return obj.industry.id

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: GlobalCommodityType):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: GlobalCommodityType):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
