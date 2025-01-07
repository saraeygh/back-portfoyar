from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from favorite.models import DomesticFavoriteRatioChartByProducer
from favorite.utils import domestic_validate_favorite_by_producer
from favorite.serializers import (
    DomesticGetFavoriteRatioChartByProducerSerailizer,
    DomesticAddFavoriteRatioChartByProducerSerailizer,
)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class DomesticFavoriteRatioChartByProducerAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        domestic_favorite_ratio_charts_by_producer = (
            user.domestic_favorite_ratio_chart_by_producer.all()
        )

        domestic_favorite_ratio_charts_by_producer_srz = (
            DomesticGetFavoriteRatioChartByProducerSerailizer(
                domestic_favorite_ratio_charts_by_producer, many=True
            )
        )

        return Response(
            domestic_favorite_ratio_charts_by_producer_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        producer_id_1 = request.data.get("company1_id")
        commodity_id_1 = request.data.get("group1_id")
        trade_commodity_name_1_id = request.data.get("commodity1_id")

        producer_id_2 = request.data.get("company2_id")
        commodity_id_2 = request.data.get("group2_id")
        trade_commodity_name_2_id = request.data.get("commodity2_id")

        validated_data_dict_1 = domestic_validate_favorite_by_producer(
            producer_id=producer_id_1,
            commodity_id=commodity_id_1,
            trade_commodity_name_id=trade_commodity_name_1_id,
        )

        validated_data_dict_2 = domestic_validate_favorite_by_producer(
            producer_id=producer_id_2,
            commodity_id=commodity_id_2,
            trade_commodity_name_id=trade_commodity_name_2_id,
        )

        if validated_data_dict_1 and validated_data_dict_2:
            validated_data_dict = {}
            user = get_object_or_404(User, id=request.user.id)
            validated_data_dict["user"] = user.id
            for key_name, value_id in validated_data_dict_1.items():
                validated_data_dict[key_name + "_1"] = value_id

            for key_name, value_id in validated_data_dict_2.items():
                validated_data_dict[key_name + "_2"] = value_id

            favorite_exists = DomesticFavoriteRatioChartByProducer.objects.filter(
                user=validated_data_dict["user"],
                producer_1=validated_data_dict["producer_1"],
                commodity_1=validated_data_dict["commodity_1"],
                trade_commodity_name_1=validated_data_dict["trade_commodity_name_1"],
                producer_2=validated_data_dict["producer_2"],
                commodity_2=validated_data_dict["commodity_2"],
                trade_commodity_name_2=validated_data_dict["trade_commodity_name_2"],
            ).exists()

            if favorite_exists:
                return Response(
                    {"message": "درخواست نامعتبر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                validated_data_dict_srz = (
                    DomesticAddFavoriteRatioChartByProducerSerailizer(
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
        favorite_ratio_chart_by_producer_id = kwargs.get("favorite_id")

        favorite_ratio_chart_by_producer = get_object_or_404(
            DomesticFavoriteRatioChartByProducer,
            id=favorite_ratio_chart_by_producer_id,
            user=request.user,
        )

        favorite_ratio_chart_by_producer.delete()

        return Response(
            {"message": "نمودار قیمت مورد علاقه پاک شد"},
            status=status.HTTP_200_OK,
        )
