import random

from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from stock_market.models.recommendation_config_model import (
    MARKETWATCH_CATEGORY,
    FUNDAMENTAL_CATEGORY,
    GLOBAL_INDEX,
    GLOBAL_INDEX_LIST,
    DOMESTIC_INDEX,
    DOMESTIC_INDEX_LIST,
    RecommendationConfig,
    MoneyFlow,
    BuyPressure,
    BuyValue,
    BuyRatio,
    SellRatio,
    ROI,
    ValueChange,
    CallValueChange,
    PutValueChange,
    OptionPriceSpread,
    GlobalPositiveRange,
    GlobalNegativeRange,
    DomesticPositiveRange,
    DomesticNegativeRange,
)


SIX_ATTR_INDICES = ["roi", "global"]
SEVEN_ATTR_INDICES = ["domestic"]


def get_configs(request):
    user_configs = {
        "config_list": list(
            request.user.configs.all().values("id", "name", "is_default")
        ),
        "default_config": {
            MARKETWATCH_CATEGORY: [],
            FUNDAMENTAL_CATEGORY: [],
        },
    }

    default_config = RecommendationConfig.objects.filter(
        user=request.user, is_default=True
    ).first()
    if default_config:
        related_config_dict = default_config.get_related_objects_as_dict_v2()

        for obj_name, obj in related_config_dict.items():
            new_index = {
                "name": obj_name,
                "is_enabled": obj.is_enabled,
                "weight": obj.weight,
                # "threshold_value": obj.threshold_value,
            }

            if obj_name in SIX_ATTR_INDICES or obj_name in SEVEN_ATTR_INDICES:
                new_index["duration"] = obj.duration
            if obj_name in SEVEN_ATTR_INDICES:
                new_index["min_commodity_ratio"] = obj.min_commodity_ratio

            user_configs["default_config"][obj.category].append(new_index)

    return user_configs


def turn_all_configs_to_non_default(user_configs):
    for user_config in user_configs:
        user_config.is_default = False
        user_config.save()


def create_new_config(user, config_name):
    if RecommendationConfig.objects.filter(user=user).count() > 4:
        return Response(
            {"message": "حداکثر تنظیمات مختلف برای هر کاربر پنج مورد است."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if RecommendationConfig.objects.filter(user=user, name=config_name).exists():
        return Response(
            {"message": "نام تکراری است."}, status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        user_configs = list(user.configs.all())
        turn_all_configs_to_non_default(user_configs)
        new_config = RecommendationConfig.objects.create(
            user=user, name=config_name, is_default=True
        )

        MoneyFlow.objects.create(recommendation=new_config, is_enabled=True)
        BuyPressure.objects.create(recommendation=new_config, is_enabled=True)
        BuyValue.objects.create(recommendation=new_config, is_enabled=True)
        BuyRatio.objects.create(recommendation=new_config, is_enabled=True)
        SellRatio.objects.create(recommendation=new_config, is_enabled=True)
        ROI.objects.create(recommendation=new_config, is_enabled=True)
        ValueChange.objects.create(recommendation=new_config, is_enabled=True)
        CallValueChange.objects.create(recommendation=new_config, is_enabled=True)
        PutValueChange.objects.create(recommendation=new_config, is_enabled=True)
        OptionPriceSpread.objects.create(recommendation=new_config, is_enabled=True)
        GlobalPositiveRange.objects.create(recommendation=new_config, is_enabled=True)
        GlobalNegativeRange.objects.create(recommendation=new_config, is_enabled=True)
        DomesticPositiveRange.objects.create(recommendation=new_config, is_enabled=True)
        DomesticNegativeRange.objects.create(recommendation=new_config, is_enabled=True)

    return Response(
        {"message": "تنظیمات با موفقیت ساخته شد"}, status=status.HTTP_200_OK
    )


def update_default_config_attrs(user, config_list):
    for config in config_list:
        is_default = config.get("is_default")
        if is_default is True:
            default_config = get_object_or_404(
                RecommendationConfig, user=user, is_default=True
            )
            change_config = get_object_or_404(
                RecommendationConfig, user=user, id=config.get("id")
            )
            if change_config.id != default_config.id:
                user_configs = list(user.configs.all())
                turn_all_configs_to_non_default(user_configs)
                change_config.is_default = is_default

            new_name = config.get("name")
            if new_name and new_name != "":
                change_config.name = new_name
            change_config.save()

    default_config = get_object_or_404(RecommendationConfig, user=user, is_default=True)
    return default_config


def update_default_config_setting(default_config: RecommendationConfig, config_data):
    config_settings = config_data.get("default_config")
    if (
        config_settings is not None
        and MARKETWATCH_CATEGORY in config_settings
        and FUNDAMENTAL_CATEGORY in config_settings
    ):
        try:
            config_settings = (
                config_settings[MARKETWATCH_CATEGORY]
                + config_settings[FUNDAMENTAL_CATEGORY]
            )

            for setting in config_settings:
                setting_name = setting.pop("name")
                if setting_name == GLOBAL_INDEX:
                    for global_index in GLOBAL_INDEX_LIST:
                        setting_obj = getattr(default_config, global_index)
                        for attr_name, attr_value in setting.items():
                            setattr(setting_obj, attr_name, attr_value)
                        setting_obj.save()

                elif setting_name == DOMESTIC_INDEX:
                    for domestic_index in DOMESTIC_INDEX_LIST:
                        setting_obj = getattr(default_config, domestic_index)
                        for attr_name, attr_value in setting.items():
                            setattr(setting_obj, attr_name, attr_value)
                        setting_obj.save()

                else:
                    setting_obj = getattr(default_config, setting_name)
                    for attr_name, attr_value in setting.items():
                        setattr(setting_obj, attr_name, attr_value)
                    setting_obj.save()

        except Exception as e:
            print(e)
            return Response(
                {"message": "مشکلی پیش آمده است"}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        {"message": "تنظیمات با موفقیت به‌روزرسانی شد‌"}, status=status.HTTP_200_OK
    )


def update_config(request):
    user = request.user
    config_data = request.data

    config_list = config_data.get("config_list")
    default_config = update_default_config_attrs(user, config_list)

    return update_default_config_setting(default_config, config_data)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockRecommendationConfigAPIViewV2(APIView):
    def get(self, request):
        configs = get_configs(request=request)
        return Response(configs, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        config_name = request.data.get("name")
        if config_name is None or config_name == "":
            return Response(
                {"message": "نام نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST
            )

        return create_new_config(user=user, config_name=config_name)

    def patch(self, request):
        return update_config(request)

    def delete(self, request):
        config_id = request.query_params.get("config_id")
        config = get_object_or_404(
            RecommendationConfig, user=request.user, id=config_id
        )
        config.delete()

        user_configs = list(request.user.configs.all())
        if user_configs:
            turn_all_configs_to_non_default(user_configs)
            random_config = random.choice(user_configs)
            random_config.is_default = True
            random_config.save()

        return Response(
            {"message": "تنظیمات مورد نظر حذف شد."}, status=status.HTTP_200_OK
        )
