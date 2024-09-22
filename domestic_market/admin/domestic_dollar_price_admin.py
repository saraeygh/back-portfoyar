import jdatetime
from django.contrib import admin
from domestic_market.models import DomesticDollarPrice


@admin.register(DomesticDollarPrice)
class DomesticDollarPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "date_shamsi", "azad", "nima")
    list_display_links = ("id", "date", "date_shamsi", "azad", "nima")
    ordering = ("-date",)
    search_fields = ("azad", "nima", "date", "date_shamsi")

    fieldsets = (
        (
            "قیمت دلار",
            {"fields": ("date", "azad", "nima")},
        ),
    )

    def save_model(self, request, obj: DomesticDollarPrice, form, change):
        obj.date_shamsi = str(jdatetime.date.fromgregorian(date=obj.date))
        return super().save_model(request, obj, form, change)
