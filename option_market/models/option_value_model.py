from django.db import models
import jdatetime as jdt

from core.models import TimeStampMixin


class OptionValue(TimeStampMixin, models.Model):
    date = models.DateField(verbose_name="تاریخ")

    call_value = models.DecimalField(
        verbose_name="ارزش کال (میلیون تومان)", max_digits=10, decimal_places=3
    )
    put_value = models.DecimalField(
        verbose_name="ارزش پوت (میلیون تومان)", max_digits=10, decimal_places=3
    )
    option_value = models.DecimalField(
        verbose_name="ارزش آپشن (میلیون تومان)", max_digits=10, decimal_places=3
    )

    put_to_call = models.DecimalField(
        verbose_name="نسبت پوت به کال", max_digits=8, decimal_places=4
    )
    option_to_market = models.DecimalField(
        verbose_name="نسبت آپشن به بازار", max_digits=8, decimal_places=4
    )

    @property
    def date_shamsi(self):
        shamsi = (jdt.datetime.fromgregorian(date=self.date)).strftime("%Y/%m/%d")
        return shamsi

    def __str__(self) -> str:
        return str(self.date)

    class Meta:
        verbose_name = "تاریخچه ارزش آپشن‌ها"
        verbose_name_plural = "۰۲) تاریخچه ارزش آپشن‌ها"
