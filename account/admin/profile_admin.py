from django.contrib import admin
from account.models import Profile, LoginCount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "id",
        "user",
        "max_login",
        "active_login",
        "phone",
        "gender",
        "birth_date",
        "created_at_shamsi",
        "updated_at_shamsi",
        "note",
    )
    list_display_links = (
        "user",
        "max_login",
        "phone",
        "gender",
        "birth_date",
    )
    ordering = ("-created_at",)

    search_fields = ("id", "user__username")

    list_filter = ("gender", "max_login", "active_login")


@admin.register(LoginCount)
class LoginCountAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "count",
        "created_at_shamsi",
        "updated_at_shamsi",
        "note",
    )
    list_display_links = ("user", "first_name", "last_name")
    ordering = ("-updated_at",)

    search_fields = ("id", "user__username", "user__first_name", "user__last_name")
