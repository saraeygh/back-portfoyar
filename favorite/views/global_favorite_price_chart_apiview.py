from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from favorite.models import GlobalFavoritePriceChart
from favorite.serializers import (
    GlobalAddFavoritePriceChartSerailizer,
    GlobalGetFavoritePriceChartSerailizer,
)
from favorite.utils import global_validate_favorite


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GlobalFavoritePriceChartAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        global_favorite_price_charts = user.global_favorite_price_chart.all()

        global_favorite_price_charts_srz = GlobalGetFavoritePriceChartSerailizer(
            global_favorite_price_charts, many=True
        )

        return Response(
            global_favorite_price_charts_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        industry_id = request.data.get("industry_id")
        commodity_type_id = request.data.get("commodity_type_id")
        commodity_id = request.data.get("commodity_id")
        transit_id = request.data.get("transit_id")

        user = get_object_or_404(User, id=request.user.id)

        validated_data_dict = global_validate_favorite(
            industry_id=industry_id,
            commodity_type_id=commodity_type_id,
            commodity_id=commodity_id,
            transit_id=transit_id,
        )

        if validated_data_dict:
            validated_data_dict["user"] = user.id

            favorite_exists = GlobalFavoritePriceChart.objects.filter(
                user=validated_data_dict["user"],
                industry=validated_data_dict["industry"],
                commodity_type=validated_data_dict["commodity_type"],
                commodity=validated_data_dict["commodity"],
                transit=validated_data_dict["transit"],
            ).exists()

            if favorite_exists:
                return Response(
                    {"message": "درخواست نامعتبر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                validated_data_dict_srz = GlobalAddFavoritePriceChartSerailizer(
                    data=validated_data_dict
                )

                validated_data_dict_srz.is_valid(raise_exception=True)
                validated_data_dict_srz.save()

                return Response(
                    {"message": "با موفقیت افزوده شد"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"message": "درخواست نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        favorite_price_chart_id = kwargs.get("favorite_price_chart_id")

        favorite_price_chart = get_object_or_404(
            GlobalFavoritePriceChart, id=favorite_price_chart_id, user=request.user
        )
        favorite_price_chart.delete()

        return Response(
            {"message": "با موفقیت پاک شد"},
            status=status.HTTP_200_OK,
        )
