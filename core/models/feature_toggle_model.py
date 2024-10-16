from django.db import models
from . import TimeStampMixin

ACTIVE = 1
DEACTIVE = 2
FEATURE_STATE = [
    (ACTIVE, "فعال"),
    (DEACTIVE, "غیرفعال"),
]


class FeatureToggle(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام ویژگی", max_length=255, unique=True)
    desc = models.TextField(verbose_name="توضیحات", blank=True, null=True)

    state = models.IntegerField(verbose_name="وضعیت", choices=FEATURE_STATE)

    value = models.CharField(
        verbose_name="مقدار ویژگی", max_length=255, blank=True, null=True
    )
