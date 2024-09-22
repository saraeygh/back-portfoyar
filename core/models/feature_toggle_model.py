from django.db import models
from . import TimeStampMixin


class FeatureToggle(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام ویژگی", max_length=255, unique=True)
    desc = models.TextField(verbose_name="توضیحات", blank=True, null=True)

    FEATURE_STATE = [(1, "فعال"), (2, "غیرفعال")]
    state = models.IntegerField(verbose_name="وضعیت", choices=FEATURE_STATE)

    value = models.CharField(
        verbose_name="مقدار ویژگی", max_length=255, blank=True, null=True
    )
