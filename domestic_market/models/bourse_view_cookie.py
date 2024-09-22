from core.models import TimeStampMixin
from django.db import models


class BourseViewCookie(TimeStampMixin, models.Model):
    cookie = models.TextField(verbose_name=("کوکی"))

    def __str__(self):
        return "cookie"

    class Meta:
        verbose_name = "کوکی"
        verbose_name_plural = "۰۸) کوکی"
