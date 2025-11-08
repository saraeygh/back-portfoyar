from django.contrib import admin

from account.models import FirstLogin


@admin.register(FirstLogin)
class FirstLoginAdmin(admin.ModelAdmin):

    autocomplete_fields = ("user",)

    list_display = (
        "id",
        "user",
        "has_logged_in",
        "created_at_shamsi",
        "updated_at_shamsi",
    )
    list_display_links = ("user",)
    ordering = ("-created_at",)

    search_fields = ("id", "user__username")

    list_filter = ("has_logged_in",)
