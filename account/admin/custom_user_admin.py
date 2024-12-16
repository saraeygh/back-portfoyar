from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_superuser",
        "is_staff",
        "is_active",
    )
    # list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    # search_fields = ("username", "first_name", "last_name", "email")

    # list_display = ("id", "username")


#     list_display_links = ("id", "username")

#     # ordering = ("-created_at",)

#     search_fields = ("id", "username")

#     # list_filter = ("gender", "max_login", "active_login", "note")
