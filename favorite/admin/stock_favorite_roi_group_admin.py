import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from favorite.models import StockFavoriteROIGroup, ROIGroupInstrument


class ROIGroupInstrumentInline(admin.StackedInline):
    model = ROIGroupInstrument
    fields = ("group", "instrument")
    autocomplete_fields = ("instrument",)
    extra = 1


@admin.register(StockFavoriteROIGroup)
class StockFavoriteROIGroupAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = ("id", "user", "name", "created_at_shamsi", "updated_at_shamsi")
    list_display_links = ("id", "name")
    ordering = ("-updated_at",)

    search_fields = ("id", "name", "user__username")

    inlines = (ROIGroupInstrumentInline,)

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: StockFavoriteROIGroup):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: StockFavoriteROIGroup):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
