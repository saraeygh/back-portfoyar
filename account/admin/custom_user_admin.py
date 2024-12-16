from django.contrib import admin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "max_login",
        "active_login",
        "note",
    )

    ordering = ("-date_joined",)

    @admin.display(description="حداکثر لاگین")
    def max_login(self, obj: User):
        return obj.profile.max_login

    @admin.display(description="لاگین فعال")
    def active_login(self, obj: User):
        return obj.profile.active_login

    @admin.display(description="توضیحات")
    def note(self, obj: User):
        return obj.profile.note


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
