from django.db import models


class Strategy(models.Model):
    name = models.CharField(verbose_name="نام استراتژی", max_length=255)

    collection_key = models.CharField(verbose_name="نام کلید", max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "استراتژی (قدیم)"
        verbose_name_plural = "۰۰) استراتژی‌ها (قدیم)"
        constraints = [
            models.UniqueConstraint(fields=["id"], name="strategy_unique_id")
        ]
