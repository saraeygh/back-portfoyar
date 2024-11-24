from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from favorite.models import DomesticFavoritePriceChartByCategory
from favorite.serializers import (
    DomesticAddFavoritePriceChartByCategorySerailizer,
    DomesticGetFavoritePriceChartByCategorySerailizer,
)
from favorite.utils import domestic_validate_favorite_by_category
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class DomesticFavoritePriceChartByCategoryAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        domestic_favorite_price_charts = (
            user.domestic_favorite_price_chart_by_category.all()
        )

        domestic_favorite_price_charts_srz = (
            DomesticGetFavoritePriceChartByCategorySerailizer(
                domestic_favorite_price_charts, many=True
            )
        )

        return Response(
            domestic_favorite_price_charts_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        industry_id = request.data.get("industry_id")
        commodity_type_id = request.data.get("field_id")
        commodity_id = request.data.get("group_id")
        producer_id = request.data.get("company_id")
        trade_commodity_name_id = request.data.get("commodity_id")

        validated_data_dict = domestic_validate_favorite_by_category(
            industry_id=industry_id,
            commodity_type_id=commodity_type_id,
            commodity_id=commodity_id,
            producer_id=producer_id,
            trade_commodity_name_id=trade_commodity_name_id,
        )

        if validated_data_dict:
            user = get_object_or_404(User, id=request.user.id)
            validated_data_dict["user"] = user.id

            favorite_exists = DomesticFavoritePriceChartByCategory.objects.filter(
                user=validated_data_dict["user"],
                industry=validated_data_dict["industry"],
                commodity_type=validated_data_dict["commodity_type"],
                commodity=validated_data_dict["commodity"],
                producer=validated_data_dict["producer"],
                trade_commodity_name=validated_data_dict["trade_commodity_name"],
            ).exists()

            if favorite_exists:
                return Response(
                    {"message": "درخواست نامعتبر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                validated_data_dict_srz = (
                    DomesticAddFavoritePriceChartByCategorySerailizer(
                        data=validated_data_dict
                    )
                )

                validated_data_dict_srz.is_valid(raise_exception=True)
                validated_data_dict_srz.save()

                return Response(
                    validated_data_dict_srz.data,
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"detail": "Invalid ids"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        favorite_price_chart_id = kwargs.get("favorite_id")

        favorite_price_chart = get_object_or_404(
            DomesticFavoritePriceChartByCategory,
            id=favorite_price_chart_id,
            user=request.user,
        )
        favorite_price_chart.delete()

        return Response(
            {"message": "نمودار قیمت مورد علاقه پاک شد"},
            status=status.HTTP_200_OK,
        )
