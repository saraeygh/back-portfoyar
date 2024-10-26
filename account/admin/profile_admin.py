from django.contrib import admin
from account.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "id",
        "user",
        "max_login",
        "active_logins",
        "phone",
        "gender",
        "birth_date",
        "created_at_shamsi",
        "updated_at_shamsi",
    )
    list_display_links = (
        "user",
        "max_login",
        "phone",
        "gender",
        "birth_date",
    )
    ordering = ("-updated_at",)

    search_fields = ("id", "user__username")

    list_filter = ("gender", "max_login")
