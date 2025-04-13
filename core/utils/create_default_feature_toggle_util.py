from core.models import FeatureToggle, ACTIVE, DEACTIVE
from colorama import Fore, Style

MARKET_STATE = {
    "name": "market_state",
    "desc": "در نظر گرفتن وضعیت بازار هنگام دریافت اطلاعات",
    "state": DEACTIVE,
    "value": "S",
}

MONTHLY_INTEREST_RATE = {
    "name": "monthly_interest_rate",
    "desc": "نرخ سود ماهانه بانکی مورد نیاز برای محاسبات قراردادهای آتی",
    "state": ACTIVE,
    "value": "2.5",
}

SEND_SIGNUP_SMS = {
    "name": "send_signup_sms_status",
    "desc": "فعال و غیرفعال کردن ارسال پیامک در صفحه ثبت‌نام",
    "state": DEACTIVE,
    "value": "",
}


SEND_RESET_PASSWORD_SMS = {
    "name": "send_reset_password_sms_status",
    "desc": "فعال و غیرفعال کردن ارسال پیامک بازنشانی رمز عبور",
    "state": DEACTIVE,
    "value": "",
}

SEND_CHANGE_USERNAME_SMS = {
    "name": "send_change_username_sms_status",
    "desc": "فعال و غیرفعال کردن ارسال پیامک تغییر نام کاربری",
    "state": DEACTIVE,
    "value": "",
}

DAILY_SIGNUP_TRY_LIMITATION = {
    "name": "daily_signup_try_limitation",
    "desc": "فعال و غیرفعال کردن محدودیت تعداد دفعات درخواست ثبت‌نام در روز از یک آی‌پی مشخص",
    "state": ACTIVE,
    "value": "3",
}

NEW_USER_FREE_DURATION = {
    "name": "new_user_free_duration",
    "desc": "مدت اشتراک رایگان برای کاربران جدید بر حسب روز",
    "state": ACTIVE,
    "value": "1",
}


def create_toggle(feature_name, feature_attr):
    if not FeatureToggle.objects.filter(name=feature_name).exists():
        FeatureToggle.objects.create(**feature_attr)
        print(Fore.GREEN + f"{feature_name} feature toggle created." + Style.RESET_ALL)
    else:
        print(
            Fore.YELLOW
            + f"{feature_name} feature toggle already exists."
            + Style.RESET_ALL
        )


def create_default_feature_toggle():

    create_toggle(MARKET_STATE["name"], MARKET_STATE)
    create_toggle(MONTHLY_INTEREST_RATE["name"], MONTHLY_INTEREST_RATE)
    create_toggle(SEND_SIGNUP_SMS["name"], SEND_SIGNUP_SMS)
    create_toggle(SEND_RESET_PASSWORD_SMS["name"], SEND_RESET_PASSWORD_SMS)
    create_toggle(SEND_CHANGE_USERNAME_SMS["name"], SEND_CHANGE_USERNAME_SMS)
    create_toggle(DAILY_SIGNUP_TRY_LIMITATION["name"], DAILY_SIGNUP_TRY_LIMITATION)
    create_toggle(NEW_USER_FREE_DURATION["name"], NEW_USER_FREE_DURATION)
