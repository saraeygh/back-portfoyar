import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from global_market.models import GlobalTrade


@admin.register(GlobalTrade)
class GlobalTradesAdmin(admin.ModelAdmin):
    autocomplete_fields = ("commodity", "transit")
    list_display = (
        "id",
        "commodity",
        "transit",
        "trade_date",
        "price",
        "created_at_shamsi",
        "updated_at_shamsi",
        "id_industry",
        "id_commodity_type",
        "id_commodity",
        "id_transit",
    )

    list_display_links = ("id", "commodity", "transit", "trade_date", "price")

    ordering = ("-trade_date", "-updated_at")

    search_fields = (
        "commodity__name",
        "transit__transit_type",
        "trade_date",
    )

    fieldsets = (
        (
            "اطلاعات کالا",
            {"fields": ("commodity",)},
        ),
        (
            "اطلاعات ترانزیت",
            {"fields": ("transit",)},
        ),
        (
            "تاریخ و قیمت معامله",
            {"fields": ("trade_date", "price")},
        ),
    )

    @admin.display(description="صنعت id")
    def id_industry(self, obj):
        return obj.commodity.commodity_type.industry.id

    @admin.display(description="نوع کالا id")
    def id_commodity_type(self, obj):
        return obj.commodity.commodity_type.id

    @admin.display(description="کالا id")
    def id_commodity(self, obj):
        return obj.commodity.id

    @admin.display(description="ترانزیت id")
    def id_transit(self, obj):
        return obj.transit.id

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: GlobalTrade):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: GlobalTrade):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
