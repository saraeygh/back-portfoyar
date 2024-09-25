from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampMixin

MARKETWATCH = 1
OPTIONS = 2
DOMESTIC = 3
GLOBAL = 4
ROI = 5
OTHER = 0
FEATURE_CHOICES = [
    (MARKETWATCH, "تابلوخوانی"),
    (OPTIONS, "قراردادهای اختیار معامله (آپشن‌ها)"),
    (DOMESTIC, "بورس کالای داخلی"),
    (GLOBAL, "بازارهای جهانی"),
    (ROI, "مقایسه سهام"),
    (OTHER, "سایر"),
]

OPEN = 0
PENDING = 1
ANSWERED = 2
CLOSED = 3
STATUS_CHOICES = [
    (OPEN, "open"),
    (PENDING, "pending"),
    (ANSWERED, "answered"),
    (CLOSED, "closed"),
]

TECHNICAL = 2
FINANCIAL = 1
UNIT_CHOICES = [
    (TECHNICAL, "فنی"),
    (FINANCIAL, "مالی"),
    (OTHER, "سایر"),
]


class Ticket(TimeStampMixin, models.Model):
    sender_user = models.ForeignKey(
        verbose_name="کاربر فرستنده",
        to=User,
        on_delete=models.CASCADE,
        related_name="sent_tickets",
    )

    receiver_user = models.ForeignKey(
        verbose_name="کاربر گیرنده",
        to=User,
        on_delete=models.CASCADE,
        related_name="received_tickets",
        blank=True,
        null=True,
    )

    unit = models.IntegerField(
        verbose_name=("واحد مربوطه"), choices=UNIT_CHOICES, default=0
    )

    feature = models.IntegerField(
        verbose_name=("بخش مربوطه"), choices=FEATURE_CHOICES, default=0
    )

    title = models.CharField(verbose_name=("عنوان"), max_length=255)

    text = models.TextField(verbose_name=("متن"), blank=True, null=True)

    status = models.IntegerField(
        verbose_name=("وضعیت"), choices=STATUS_CHOICES, default=0
    )

    file = models.CharField(
        verbose_name="فایل ضمیمه", max_length=255, blank=True, null=True
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "تیکت‌"
        verbose_name_plural = "۰۱) تیکت‌ها"


class TicketResponse(TimeStampMixin, models.Model):
    ticket = models.ForeignKey(
        verbose_name="تیکت",
        to=Ticket,
        on_delete=models.CASCADE,
        related_name="responses",
    )

    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="ticket_responses",
    )

    text = models.TextField(verbose_name=("متن"), blank=True, null=True)

    file = models.CharField(
        verbose_name="فایل ضمیمه", max_length=255, blank=True, null=True
    )

    def __str__(self):
        return f"{self.ticket.title}"

    class Meta:
        verbose_name = "پاسخ تیکت"
        verbose_name_plural = "۰۲) پاسخ‌های تیکت‌ها"
