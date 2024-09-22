import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from domestic_market.models import DomesticCommodity


@admin.register(DomesticCommodity)
class DomesticCommodityAdmin(admin.ModelAdmin):
    autocomplete_fields = ("commodity_type",)
    list_display = (
        "id",
        "commodity_type",
        "name",
        "code",
        "created_at_shamsi",
        "updated_at_shamsi",
        "id_commodity_type",
        "commodity_type_code",
    )

    list_display_links = ("id", "commodity_type", "name", "code")

    ordering = ("-updated_at",)

    search_fields = ("commodity_type__name", "name", "code")

    @admin.display(description="نوع کالا id")
    def id_commodity_type(self, obj):
        return obj.commodity_type.id

    @admin.display(description="کد نوع کالا")
    def commodity_type_code(self, obj):
        return obj.commodity_type.code

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticCommodity):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticCommodity):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
