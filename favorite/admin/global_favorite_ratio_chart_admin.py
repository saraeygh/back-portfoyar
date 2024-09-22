import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from favorite.models import GlobalFavoriteRatioChart


@admin.register(GlobalFavoriteRatioChart)
class GlobalFavoriteRatioChartAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "user",
        "industry_1",
        "commodity_type_1",
        "commodity_1",
        "transit_1",
        "industry_2",
        "commodity_type_2",
        "commodity_2",
        "transit_2",
    )

    list_display = (
        "id",
        "user",
        "id_industry_1",
        "id_commodity_type_1",
        "id_commodity_1",
        "id_transit_1",
        "id_industry_2",
        "id_commodity_type_2",
        "id_commodity_2",
        "id_transit_2",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "id",
        "user",
        "id_industry_1",
        "id_industry_2",
        "id_commodity_type_1",
        "id_commodity_type_2",
        "id_commodity_1",
        "id_commodity_2",
        "id_transit_1",
        "id_transit_2",
    )

    ordering = ("-updated_at",)

    search_fields = ("user__username",)

    @admin.display(description="صنعت ۱ id")
    def id_industry_1(self, obj):
        return obj.industry_1.id

    @admin.display(description="صنعت ۲ id")
    def id_industry_2(self, obj):
        return obj.industry_2.id

    @admin.display(description="نوع کالا ۱ id")
    def id_commodity_type_1(self, obj):
        return obj.commodity_type_1.id

    @admin.display(description="نوع کالا ۲ id")
    def id_commodity_type_2(self, obj):
        return obj.commodity_type_2.id

    @admin.display(description="کالا ۱ id")
    def id_commodity_1(self, obj):
        if obj.commodity_1:
            return obj.commodity_1.id
        return None

    @admin.display(description="کالا ۲ id")
    def id_commodity_2(self, obj):
        if obj.commodity_2:
            return obj.commodity_2.id
        return None

    @admin.display(description="ترانزیت ۱ id")
    def id_transit_1(self, obj):
        if obj.transit_1:
            return obj.transit_1.id
        return None

    @admin.display(description="ترانزیت ۲ id")
    def id_transit_2(self, obj):
        if obj.transit_2:
            return obj.transit_2.id
        return None

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: GlobalFavoriteRatioChart):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: GlobalFavoriteRatioChart):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
