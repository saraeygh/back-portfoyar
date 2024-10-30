from core.models import FeatureToggle, ACTIVE, DEACTIVE
from colorama import Fore, Style

MARKET_STATE = "market_state"

MONTHLY_INTEREST_RATE_NAME = "monthly_interest_rate"
MONTHLY_INTEREST_RATE_VALUE = "2.5"

SEND_SIGNUP_SMS_STATUS = "send_signup_sms_status"

DAILY_SIGNUP_TRY_LIMITATION = "daily_signup_try_limitation"


def create_default_feature_toggle():

    if not FeatureToggle.objects.filter(name=MARKET_STATE).exists():
        FeatureToggle.objects.create(
            name=MARKET_STATE,
            desc="در نظر گرفتن وضعیت بازار هنگام دریافت اطلاعات",
            state=DEACTIVE,
            value="S",
        )
        print(Fore.GREEN + f"{MARKET_STATE} feature toggle created." + Style.RESET_ALL)
    else:
        print(
            Fore.YELLOW
            + f"{MARKET_STATE} feature toggle already exists."
            + Style.RESET_ALL
        )

    ###########################################################################
    if not FeatureToggle.objects.filter(name=MONTHLY_INTEREST_RATE_NAME).exists():
        FeatureToggle.objects.create(
            name=MONTHLY_INTEREST_RATE_NAME,
            desc="نرخ سود ماهانه بانکی مورد نیاز برای محاسبات قراردادهای آتی",
            state=ACTIVE,
            value=MONTHLY_INTEREST_RATE_VALUE,
        )
        print(
            Fore.GREEN
            + f"{MONTHLY_INTEREST_RATE_NAME} feature toggle created."
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + f"{MONTHLY_INTEREST_RATE_NAME} feature toggle already exists."
            + Style.RESET_ALL
        )
    ###########################################################################
    if not FeatureToggle.objects.filter(name=SEND_SIGNUP_SMS_STATUS).exists():
        FeatureToggle.objects.create(
            name=SEND_SIGNUP_SMS_STATUS,
            desc="فعال و غیرفعال کردن ارسال پیامک در صفحه ثبت‌نام",
            state=DEACTIVE,
            value=SEND_SIGNUP_SMS_STATUS,
        )
        print(
            Fore.GREEN
            + f"{SEND_SIGNUP_SMS_STATUS} feature toggle created."
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + f"{SEND_SIGNUP_SMS_STATUS} feature toggle already exists."
            + Style.RESET_ALL
        )

    ###########################################################################
    if not FeatureToggle.objects.filter(name=DAILY_SIGNUP_TRY_LIMITATION).exists():
        FeatureToggle.objects.create(
            name=DAILY_SIGNUP_TRY_LIMITATION,
            desc="فعال و غیرفعال کردن محدودیت تعداد دفعات درخواست ثبت‌نام در روز از یک آی‌پی مشخص",
            state=ACTIVE,
            value=DAILY_SIGNUP_TRY_LIMITATION,
        )
        print(
            Fore.GREEN
            + f"{DAILY_SIGNUP_TRY_LIMITATION} feature toggle created."
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + f"{DAILY_SIGNUP_TRY_LIMITATION} feature toggle already exists."
            + Style.RESET_ALL
        )
