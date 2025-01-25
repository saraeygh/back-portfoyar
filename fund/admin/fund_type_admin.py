from django.contrib import admin
from fund.models import FundType


@admin.register(FundType)
class FundTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active")
    list_display_links = ("name",)
    ordering = ("-created_at",)

    search_fields = ("code", "name")

    list_filter = ("is_active",)
