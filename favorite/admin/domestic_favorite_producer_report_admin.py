import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from favorite.models import DomesticFavoriteProducerReport


@admin.register(DomesticFavoriteProducerReport)
class DomesticFavoriteProducerReportAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "user",
        "producer",
    )

    list_display = (
        "id",
        "user",
        "id_producer",
        "producer",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = (
        "id",
        "user",
        "producer",
    )

    ordering = ("-updated_at",)

    search_fields = ("user__username",)

    @admin.display(description="تولید کننده id")
    def id_producer(self, obj):
        if obj.producer:
            return obj.producer.id
        return None

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: DomesticFavoriteProducerReport):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: DomesticFavoriteProducerReport):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
