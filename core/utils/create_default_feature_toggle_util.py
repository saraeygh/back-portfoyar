from core.models import FeatureToggle


def create_default_feature_toggle():

    if not FeatureToggle.objects.filter(name="market_state").exists():
        FeatureToggle.objects.create(
            name="market_state",
            desc="در نظر گرفتن وضعیت بازار هنگام دریافت اطلاعات",
            state=2,
            value="S",
        )
        print("market_state feature toggle created.")
    else:
        print("market_state feature toggle already exists.")
