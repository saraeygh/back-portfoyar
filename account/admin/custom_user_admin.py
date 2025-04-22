from django.contrib import admin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

import jdatetime as jdt
from core.configs import TEHRAN_TZ


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
        "date_joined_shamsi",
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

    @admin.display(description="عضویت")
    def date_joined_shamsi(self, obj: User):
        shamsi = (
            jdt.datetime.fromgregorian(datetime=obj.date_joined, tzinfo=TEHRAN_TZ)
            + jdt.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")
        return shamsi


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
