from django.contrib.auth.models import User
from django.db import models
from core.models import TimeStampMixin
from option_market.models import Strategy


class OptionsFavoriteSymbol(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="options_favorite_symbols",
    )

    strategy = models.ForeignKey(
        verbose_name="استراتژی", to=Strategy, on_delete=models.CASCADE
    )

    symbol = models.CharField(verbose_name="نماد مورد علاقه", max_length=255)

    class Meta:
        verbose_name = "Options: نماد مورد علاقه"
        verbose_name_plural = "Options: نمادهای مورد علاقه"
        unique_together = ("user", "strategy", "symbol")
