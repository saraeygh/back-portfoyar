from rest_framework import serializers
from core.serializers import RoundedFloatField
from core.configs import STOCK_NA_ROI, STOCK_NO_ROI_LETTER


class MarketROISerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()

    daily_roi = RoundedFloatField(decimal_places=2)
    weekly_roi = RoundedFloatField(decimal_places=0)
    monthly_roi = RoundedFloatField(decimal_places=0)
    quarterly_roi = RoundedFloatField(decimal_places=0)
    half_yearly_roi = RoundedFloatField(decimal_places=0)
    yearly_roi = RoundedFloatField(decimal_places=0)
    three_years_roi = RoundedFloatField(decimal_places=0)

    market_cap = RoundedFloatField(decimal_places=0)
    pe = RoundedFloatField(decimal_places=2)
    sector_pe = RoundedFloatField(decimal_places=2)
    ps = RoundedFloatField(decimal_places=2)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["daily_roi"] == STOCK_NA_ROI:
            representation["daily_roi"] = STOCK_NO_ROI_LETTER
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


class SummaryMarketROISerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    link = serializers.CharField()
    symbol = serializers.CharField()

    weekly_roi = RoundedFloatField(decimal_places=0)
    monthly_roi = RoundedFloatField(decimal_places=0)
    quarterly_roi = RoundedFloatField(decimal_places=0)
    half_yearly_roi = RoundedFloatField(decimal_places=0)
    yearly_roi = RoundedFloatField(decimal_places=0)

    pe = RoundedFloatField(decimal_places=2)
    sector_pe = RoundedFloatField(decimal_places=2)
    ps = RoundedFloatField(decimal_places=2)

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

        return representation


class FavoriteGroupMarketROISerailizer(MarketROISerailizer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        group_id = self.context.get("group_id")
        representation["group_id"] = group_id

        return representation
