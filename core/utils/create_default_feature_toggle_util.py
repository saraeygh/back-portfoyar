from core.models import FeatureToggle, ACTIVE, DEACTIVE

MARKET_STATE = "market_state"

MONTHLY_INTEREST_RATE_NAME = "monthly_interest_rate"
MONTHLY_INTEREST_RATE_VALUE = "2.5"


def create_default_feature_toggle():

    if not FeatureToggle.objects.filter(name=MARKET_STATE).exists():
        FeatureToggle.objects.create(
            name=MARKET_STATE,
            desc="در نظر گرفتن وضعیت بازار هنگام دریافت اطلاعات",
            state=DEACTIVE,
            value="S",
        )
        print(f"{MARKET_STATE} feature toggle created.")
    else:
        print(f"{MARKET_STATE} feature toggle already exists.")

    ###########################################################################
    if not FeatureToggle.objects.filter(name=MONTHLY_INTEREST_RATE_NAME).exists():
        FeatureToggle.objects.create(
            name=MONTHLY_INTEREST_RATE_NAME,
            desc="نرخ سود ماهانه بانکی مورد نیاز برای محاسبات قراردادهای آتی",
            state=ACTIVE,
            value=MONTHLY_INTEREST_RATE_VALUE,
        )
        print(f"{MONTHLY_INTEREST_RATE_NAME} feature toggle created.")
    else:
        print(f"{MONTHLY_INTEREST_RATE_NAME} feature toggle already exists.")
