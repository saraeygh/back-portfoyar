import jdatetime as jdt

from django.contrib import admin

from core.configs import TEHRAN_TZ

from payment.models import Receipt, NotConfirmedReceipt, ConfirmedReceipt


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request)

    list_display = (
        "id",
        "user",
        "feature",
        "discount_object",
        "discount_id",
        "receipt_id",
        "price",
        "method",
        "is_confirmed",
        "description",
        "pay_id",
        "tracking_id",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "user", "method", "description")

    ordering = ("-created_at",)

    search_fields = (
        "user__username",
        "receipt_id",
        "feature__name",
        "discount_object__name",
        "method",
        "pay_id",
        "tracking_id",
        "description",
    )

    list_filter = ("is_confirmed", "method")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: Receipt):
        shamsi = jdt.datetime.fromgregorian(
            datetime=obj.created_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: Receipt):
        shamsi = jdt.datetime.fromgregorian(
            datetime=obj.updated_at, tzinfo=TEHRAN_TZ
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi


@admin.register(NotConfirmedReceipt)
class NotConfirmedReceiptAdmin(ReceiptAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_confirmed=False)


@admin.register(ConfirmedReceipt)
class ConfirmedReceiptAdmin(ReceiptAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_confirmed=True)
