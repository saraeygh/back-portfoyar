import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from favorite.models import DomesticFavoritePriceChartByCategory


@admin.register(DomesticFavoritePriceChartByCategory)
class DomesticFavoritePriceChartByCategoryAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "user",
        "industry",
        "commodity_type",
        "commodity",
        "producer",
        "trade_commodity_name",
    )
    list_display = (
        "id",
        "user",
        "id_industry",
        "industry",
        "id_commodity_type",
        "commodity_type",
        "id_commodity",
        "commodity",
        "id_producer",
        "producer",
        "id_trade_commodity_name",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "id",
        "user",
        "industry",
        "commodity_type",
        "commodity",
        "producer",
    )

    ordering = ("-updated_at",)

    search_fields = ("user__username",)

    @admin.display(description="صنعت id")
    def id_industry(self, obj):
        return obj.industry.id

    @admin.display(description="نوع کالا id")
    def id_commodity_type(self, obj):
        return obj.commodity_type.id

    @admin.display(description="کالا id")
    def id_commodity(self, obj):
        if obj.commodity:
            return obj.commodity.id
        return None

    @admin.display(description="تولید کننده id")
    def id_producer(self, obj):
        if obj.producer:
            return obj.producer.id
        return None

    @admin.display(description="نام کالا")
    def id_trade_commodity_name(self, obj):
        if obj.trade_commodity_name:
            return f"{obj.trade_commodity_name.id}: {obj.trade_commodity_name.commodity_name}"
        return None

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticFavoritePriceChartByCategory):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticFavoritePriceChartByCategory):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
