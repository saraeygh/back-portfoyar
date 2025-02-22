from rest_framework import serializers
from core.serializers import RoundedFloatField
from core.configs import STOCK_NA_ROI, STOCK_NO_ROI_LETTER


class IndustryROISerailizer(serializers.Serializer):
    industrial_group_id = serializers.IntegerField()
    industrial_group_name = serializers.CharField()

    weekly_roi = RoundedFloatField(decimal_places=0)
    monthly_roi = RoundedFloatField(decimal_places=0)
    quarterly_roi = RoundedFloatField(decimal_places=0)
    half_yearly_roi = RoundedFloatField(decimal_places=0)
    yearly_roi = RoundedFloatField(decimal_places=0)
    three_years_roi = RoundedFloatField(decimal_places=0)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["weekly_roi"] == STOCK_NA_ROI:
            representation["weekly_roi"] = STOCK_NO_ROI_LETTER
        if representation["monthly_roi"] == STOCK_NA_ROI:
            representation["monthly_roi"] = STOCK_NO_ROI_LETTER
        if representation["quarterly_roi"] == STOCK_NA_ROI:
            representation["quarterly_roi"] = STOCK_NO_ROI_LETTER
        if representation["half_yearly_roi"] == STOCK_NA_ROI:
            representation["half_yearly_roi"] = STOCK_NO_ROI_LETTER
        if representation["yearly_roi"] == STOCK_NA_ROI:
            representation["yearly_roi"] = STOCK_NO_ROI_LETTER
        if representation["three_years_roi"] == STOCK_NA_ROI:
            representation["three_years_roi"] = STOCK_NO_ROI_LETTER

        return representation


class DashboardIndustryROISerailizer(serializers.Serializer):
    industrial_group_name = serializers.CharField()

    weekly_roi = RoundedFloatField(decimal_places=0)
    monthly_roi = RoundedFloatField(decimal_places=0)
    quarterly_roi = RoundedFloatField(decimal_places=0)
    half_yearly_roi = RoundedFloatField(decimal_places=0)
    yearly_roi = RoundedFloatField(decimal_places=0)
    three_years_roi = RoundedFloatField(decimal_places=0)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["weekly_roi"] == STOCK_NA_ROI:
            representation["weekly_roi"] = STOCK_NO_ROI_LETTER
        if representation["monthly_roi"] == STOCK_NA_ROI:
            representation["monthly_roi"] = STOCK_NO_ROI_LETTER
        if representation["quarterly_roi"] == STOCK_NA_ROI:
            representation["quarterly_roi"] = STOCK_NO_ROI_LETTER
        if representation["half_yearly_roi"] == STOCK_NA_ROI:
            representation["half_yearly_roi"] = STOCK_NO_ROI_LETTER
        if representation["yearly_roi"] == STOCK_NA_ROI:
            representation["yearly_roi"] = STOCK_NO_ROI_LETTER
        if representation["three_years_roi"] == STOCK_NA_ROI:
            representation["three_years_roi"] = STOCK_NO_ROI_LETTER

        return representation
