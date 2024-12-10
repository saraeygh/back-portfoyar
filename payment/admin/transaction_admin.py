import jdatetime as jdt

from django.contrib import admin

from core.configs import TEHRAN_TZ

from payment.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tx_id",
        "price",
        "method",
        "is_confirmed",
        "description",
        "pay_id",
        "tracking_id",
        "plan",
        "discount",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "user", "method", "description")

    ordering = ("created_at",)

    search_fields = (
        "user__username",
        "tx_id",
        "plan",
        "discount",
        "method",
        "pay_id",
        "tracking_id",
        "description",
    )

    list_filter = ("is_confirmed", "method")

    readonly_fields = (
        "id",
        "user",
        "tx_id",
        "plan",
        "discount",
        "price",
        "method",
        "pay_id",
        "is_confirmed",
        "tracking_id",
    )

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: Transaction):
        shamsi = jdt.datetime.fromgregorian(
            datetime=obj.created_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: Transaction):
        shamsi = jdt.datetime.fromgregorian(
            datetime=obj.updated_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
