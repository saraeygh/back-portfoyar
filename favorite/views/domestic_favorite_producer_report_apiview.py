from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from domestic_market.models import DomesticProducer
from favorite.models import DomesticFavoriteProducerReport
from favorite.serializers import (
    DomesticAddFavoriteProducerReportSerailizer,
    DomesticGetFavoriteProducerReportSerailizer,
)
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class DomesticFavoriteProducerReportAPIView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        domestic_favorite_producer_sell = user.domestic_favorite_producer_report.all()

        domestic_favorite_producer_sell_srz = (
            DomesticGetFavoriteProducerReportSerailizer(
                domestic_favorite_producer_sell, many=True
            )
        )

        return Response(
            domestic_favorite_producer_sell_srz.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        producer_id = request.data.get("producer")
        producer = get_object_or_404(DomesticProducer, id=producer_id)
        user = get_object_or_404(User, id=request.user.id)
        new_favorite = {"user": user.id, "producer": producer_id}

        favorite_exists = DomesticFavoriteProducerReport.objects.filter(
            user=user,
            producer=producer,
        ).exists()

        if favorite_exists:
            return Response(
                {"message": "درخواست نامعتبر"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            favorite_srz = DomesticAddFavoriteProducerReportSerailizer(
                data=new_favorite
            )

            favorite_srz.is_valid(raise_exception=True)
            favorite_srz.save()

            return Response(
                favorite_srz.data,
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        favorite_producer_report_id = kwargs.get("favorite_id")

        favorite_producer_report = get_object_or_404(
            DomesticFavoriteProducerReport,
            id=favorite_producer_report_id,
            user=request.user,
        )
        favorite_producer_report.delete()

        return Response(
            {"message": "نمودار قیمت مورد علاقه پاک شد"},
            status=status.HTTP_200_OK,
        )
