import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from favorite.models import DomesticFavoriteRatioChartByProducer


@admin.register(DomesticFavoriteRatioChartByProducer)
class DomesticFavoriteRatioChartByProducerAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "user",
        "producer_1",
        "commodity_1",
        "trade_commodity_name_1",
        "producer_2",
        "commodity_2",
        "trade_commodity_name_2",
    )

    list_display = (
        "id",
        "user",
        "id_producer_1",
        "id_commodity_1",
        "id_trade_commodity_name_1",
        "id_producer_2",
        "id_commodity_2",
        "id_trade_commodity_name_2",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "id",
        "user",
        "id_producer_1",
        "id_producer_2",
        "id_commodity_1",
        "id_commodity_2",
    )

    ordering = ("-updated_at",)

    search_fields = ("user__username",)

    @admin.display(description="تولید کننده ۱ id")
    def id_producer_1(self, obj):
        if obj.producer_1:
            return obj.producer_1.id
        return None

    @admin.display(description="تولید کننده ۲ id")
    def id_producer_2(self, obj):
        if obj.producer_2:
            return obj.producer_2.id
        return None

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

    @admin.display(description="نام کالا ۱")
    def id_trade_commodity_name_1(self, obj):
        if obj.trade_commodity_name_1:
            return f"{obj.trade_commodity_name_1.id}: {obj.trade_commodity_name_1.commodity_name}"
        return None

    @admin.display(description="نام کالا ۲")
    def id_trade_commodity_name_2(self, obj):
        if obj.trade_commodity_name_2:
            return f"{obj.trade_commodity_name_2.id}: {obj.trade_commodity_name_2.commodity_name}"
        return None

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticFavoriteRatioChartByProducer):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticFavoriteRatioChartByProducer):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
