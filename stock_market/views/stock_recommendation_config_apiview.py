from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from stock_market.models.recommendation_config_model import (
    CATEGORY_CHOICES,
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
from colorama import Fore, Style

categories = [category[0] for category in CATEGORY_CHOICES]


SIX_ATTRIBUTES_INDICES = ["roi", "global_positive_range", "global_negative_range"]

SEVEN_ATTRIBUTES_INDICES = ["domestic_positive_range", "domestic_negative_range"]


def get_configs(configs: list):
    config_list = list()
    for config in configs:
        config_dict = {
            "id": config.id,
            "name": config.name,
            "is_default": config.is_default,
        }
        for category in categories:
            config_dict[category] = list()

        related_config_dict = config.get_related_objects_as_dict()

        for obj_name, obj in related_config_dict.items():
            new_index = {
                "name": obj_name,
                "is_enabled": obj.is_enabled,
                "weight": obj.weight,
            }

            config_dict[obj.category].append(new_index)

        config_list.append(config_dict)

    return config_list


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

    new_config = RecommendationConfig.objects.create(user=user, name=config_name)
    if not RecommendationConfig.objects.filter(user=user, is_default=True).exists():
        new_config.is_default = True
        new_config.save()
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

    configs = list(user.configs.all().order_by("created_at"))
    configs = get_configs(configs=configs)

    return Response(configs, status=status.HTTP_200_OK)


def update_related_objects(config_id, request):
    config = get_object_or_404(RecommendationConfig, id=config_id)
    related_dicts = request.data

    try:
        for related_dict in related_dicts:
            related_obj = getattr(config, related_dict["name"])
            setattr(related_obj, "is_enabled", related_dict["is_enabled"])
            weight = related_dict.get("weight")
            if weight:
                setattr(related_obj, "weight", weight)
            related_obj.save()
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return Response(
            {"message": "مشکلی پیش آمده است"}, status=status.HTTP_400_BAD_REQUEST
        )

    configs = list(request.user.configs.all())
    configs = get_configs(configs=configs)

    return Response(configs, status=status.HTTP_200_OK)


def update_config(request, config_id):
    try:
        is_default = request.data.get("is_default")

        default_config_obj = get_object_or_404(
            RecommendationConfig, user=request.user, is_default=True
        )
        update_config_obj = get_object_or_404(RecommendationConfig, id=config_id)
        if update_config_obj.id != default_config_obj.id and is_default is True:
            user_configs = list(request.user.configs.all())
            for config in user_configs:
                config.is_default = False
                config.save()
            update_config_obj.is_default = is_default

        new_name = request.data.get("name")
        if new_name:
            update_config_obj.name = new_name
        update_config_obj.save()

        configs = list(request.user.configs.all().order_by("created_at"))
        configs = get_configs(configs=configs)
        return Response(configs, status=status.HTTP_200_OK)

    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return Response(
            {"message": "مشکلی پیش آمده است"}, status=status.HTTP_400_BAD_REQUEST
        )


def get_setting(config, setting_name):
    obj = getattr(config, setting_name)

    if setting_name in SIX_ATTRIBUTES_INDICES:
        setting = {
            "name": setting_name,
            "weight": obj.weight,
            "threshold_value": obj.threshold_value,
            "duration": obj.duration,
        }

    elif setting_name in SEVEN_ATTRIBUTES_INDICES:
        setting = {
            "name": setting_name,
            "weight": obj.weight,
            "threshold_value": obj.threshold_value,
            "duration": obj.duration,
            "min_commodity_ratio": obj.min_commodity_ratio,
        }
    else:
        setting = {
            "name": setting_name,
            "weight": obj.weight,
            "threshold_value": obj.threshold_value,
        }

    return setting


def update_setting(config, setting_name, request):
    related_obj = getattr(config, setting_name)
    new_setting_data = request.data

    if setting_name in SIX_ATTRIBUTES_INDICES:
        attr_names = ["weight", "threshold_value", "duration"]
        for attr_name in attr_names:
            if attr_name in new_setting_data:
                setattr(related_obj, attr_name, new_setting_data[attr_name])
                related_obj.save()
    elif setting_name in SEVEN_ATTRIBUTES_INDICES:
        attr_names = ["weight", "threshold_value", "duration", "min_commodity_ratio"]
        for attr_name in attr_names:
            if attr_name in new_setting_data:
                setattr(related_obj, attr_name, new_setting_data[attr_name])
                related_obj.save()
    else:
        attr_names = ["weight", "threshold_value"]
        for attr_name in attr_names:
            if attr_name in new_setting_data:
                setattr(related_obj, attr_name, new_setting_data[attr_name])
                related_obj.save()

    return Response({"message": "تنظیمات به‌روزرسانی شد."}, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockRecommendationConfigAPIView(APIView):
    def get(self, request):
        configs = list(request.user.configs.all().order_by("created_at"))
        configs = get_configs(configs=configs)

        return Response(configs, status=status.HTTP_200_OK)

    def post(self, request):
        config_name = request.data.get("name")
        if config_name is None or config_name == "":
            return Response(
                {"message": "نام نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST
            )

        return create_new_config(user=request.user, config_name=config_name)

    def patch(self, request, config_id):
        return update_config(request, config_id)

    def put(self, request, config_id):

        return update_related_objects(config_id, request)

    def delete(self, request, config_id):
        config = get_object_or_404(RecommendationConfig, id=config_id)
        config.delete()

        configs = request.user.configs
        if configs.exists():
            random_config = configs.first()
            random_config.is_default = True
            random_config.save()

        return Response(
            {"message": "تنظیمات مورد نظر حذف شد."}, status=status.HTTP_200_OK
        )


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockRecommendationConfigSettingAPIView(APIView):
    def get(self, request, config_id, setting_name):
        config = get_object_or_404(RecommendationConfig, id=config_id)
        setting = get_setting(config, setting_name)

        return Response(setting, status=status.HTTP_200_OK)

    def patch(self, request, config_id, setting_name):
        config = get_object_or_404(RecommendationConfig, id=config_id)
        return update_setting(config, setting_name, request)
