import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from rest_framework.authtoken.models import Token
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

    @admin.display(description="ورودهای قعال")
    def active_logins(self, obj: Profile):
        logins = Token.objects.filter(user=obj.user).count()
        return logins

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: Profile):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: Profile):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
