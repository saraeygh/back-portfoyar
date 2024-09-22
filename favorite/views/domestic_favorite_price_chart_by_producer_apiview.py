from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from favorite.models import DomesticFavoritePriceChartByProducer
from favorite.serializers import (
    DomesticAddFavoritePriceChartByProducerSerailizer,
    DomesticGetFavoritePriceChartByProducerSerailizer,
)
from favorite.utils import domestic_validate_favorite_by_producer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class DomesticFavoritePriceChartByProducerAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        domestic_favorite_price_charts_by_producer = (
            user.domestic_favorite_price_chart_by_producer.all()
        )

        domestic_favorite_price_charts_by_producer_srz = (
            DomesticGetFavoritePriceChartByProducerSerailizer(
                domestic_favorite_price_charts_by_producer, many=True
            )
        )

        return Response(
            domestic_favorite_price_charts_by_producer_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        producer_id = request.data.get("company_id")
        commodity_id = request.data.get("group_id")
        trade_commodity_name_id = request.data.get("commodity_id")

        validated_data_dict = domestic_validate_favorite_by_producer(
            producer_id=producer_id,
            commodity_id=commodity_id,
            trade_commodity_name_id=trade_commodity_name_id,
        )

        if validated_data_dict:
            user = get_object_or_404(User, id=request.user.id)
            validated_data_dict["user"] = user.id

            favorite_exists = DomesticFavoritePriceChartByProducer.objects.filter(
                user=validated_data_dict["user"],
                producer=validated_data_dict["producer"],
                commodity=validated_data_dict["commodity"],
                trade_commodity_name=validated_data_dict["trade_commodity_name"],
            ).exists()

            if favorite_exists:
                return Response(
                    {"message": "درخواست نامعتبر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:
                validated_data_dict_srz = (
                    DomesticAddFavoritePriceChartByProducerSerailizer(
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
        favorite_price_chart_by_producer_id = kwargs.get("favorite_id")

        favorite_price_chart_by_producer = get_object_or_404(
            DomesticFavoritePriceChartByProducer,
            id=favorite_price_chart_by_producer_id,
        )
        favorite_price_chart_by_producer.delete()

        return Response(
            {"message": "نمودار قیمت مورد علاقه پاک شد"},
            status=status.HTTP_200_OK,
        )
