from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from favorite.models import GlobalFavoriteRatioChart
from favorite.serializers import (
    GlobalAddFavoriteRatioChartSerailizer,
    GlobalGetFavoriteRatioChartSerailizer,
)
from favorite.utils import global_validate_favorite
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GlobalFavoriteRatioChartAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        global_favorite_ratio_charts = user.global_favorite_ratio_chart.all()

        global_favorite_ratio_charts_srz = GlobalGetFavoriteRatioChartSerailizer(
            global_favorite_ratio_charts, many=True
        )

        return Response(
            global_favorite_ratio_charts_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        industry_id_1 = request.data.get("industry_1_id")
        commodity_type_id_1 = request.data.get("commodity_type_1_id")
        commodity_id_1 = request.data.get("commodity_1_id")
        transit_id_1 = request.data.get("transit_1_id")

        industry_id_2 = request.data.get("industry_2_id")
        commodity_type_id_2 = request.data.get("commodity_type_2_id")
        commodity_id_2 = request.data.get("commodity_2_id")
        transit_id_2 = request.data.get("transit_2_id")

        validated_data_dict_1 = global_validate_favorite(
            industry_id=industry_id_1,
            commodity_type_id=commodity_type_id_1,
            commodity_id=commodity_id_1,
            transit_id=transit_id_1,
        )

        validated_data_dict_2 = global_validate_favorite(
            industry_id=industry_id_2,
            commodity_type_id=commodity_type_id_2,
            commodity_id=commodity_id_2,
            transit_id=transit_id_2,
        )

        user = get_object_or_404(User, id=request.user.id)
        if validated_data_dict_1 and validated_data_dict_2:
            validated_data_dict = {}
            validated_data_dict["user"] = user.id
            for key_name, value_id in validated_data_dict_1.items():
                validated_data_dict[key_name + "_1"] = value_id

            for key_name, value_id in validated_data_dict_2.items():
                validated_data_dict[key_name + "_2"] = value_id

            favorite_exists = GlobalFavoriteRatioChart.objects.filter(
                user=validated_data_dict["user"],
                industry_1=validated_data_dict["industry_1"],
                commodity_type_1=validated_data_dict["commodity_type_1"],
                commodity_1=validated_data_dict["commodity_1"],
                transit_1=validated_data_dict["transit_1"],
                industry_2=validated_data_dict["industry_2"],
                commodity_type_2=validated_data_dict["commodity_type_2"],
                commodity_2=validated_data_dict["commodity_2"],
                transit_2=validated_data_dict["transit_2"],
            ).exists()

            if favorite_exists:
                return Response(
                    {"message": "درخواست نامعتبر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                validated_data_dict_srz = GlobalAddFavoriteRatioChartSerailizer(
                    data=validated_data_dict
                )

                validated_data_dict_srz.is_valid(raise_exception=True)
                validated_data_dict_srz.save()

                return Response(
                    validated_data_dict_srz.data,
                    status=status.HTTP_200_OK,
                )

    def delete(self, request, *args, **kwargs):
        favorite_ratio_chart_id = kwargs.get("favorite_ratio_chart_id")

        favorite_ratio_chart = get_object_or_404(
            GlobalFavoriteRatioChart,
            id=favorite_ratio_chart_id,
        )

        favorite_ratio_chart.delete()

        return Response(
            {"message": "نمودار قیمت مورد علاقه پاک شد"},
            status=status.HTTP_200_OK,
        )
