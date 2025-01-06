from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from domestic_market.models import DomesticProducer

from favorite.models import DomesticFavoriteProducerReport
from favorite.serializers import DomesticGetFavoriteProducerReportSerailizer


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
            domestic_favorite_producer_sell_srz.data, status=status.HTTP_200_OK
        )

    def post(self, request):
        producer_id = request.data.get("producer")
        producer = get_object_or_404(DomesticProducer, id=producer_id)
        user = get_object_or_404(User, id=request.user.id)

        try:
            DomesticFavoriteProducerReport.objects.get(user=user, producer=producer)
            return Response(
                {"message": "تولید کننده تکراری است"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DomesticFavoriteProducerReport.DoesNotExist:
            new_favorite = {"user": user, "producer": producer}
            DomesticFavoriteProducerReport.objects.create(**new_favorite)
            return Response(
                {"message": "تولید کننده اضافه شد"}, status=status.HTTP_200_OK
            )

    def delete(self, request, *args, **kwargs):
        favorite_id = kwargs.get("favorite_id")
        try:
            favorite = DomesticFavoriteProducerReport.objects.get(
                id=favorite_id, user=request.user
            )
            favorite.delete()
            return Response(
                {"message": "تولید کننده مورد نظر حذف شد"}, status=status.HTTP_200_OK
            )
        except DomesticFavoriteProducerReport.DoesNotExist:
            return Response(
                {"message": "تولید کننده وجود ندارد"},
                status=status.HTTP_400_BAD_REQUEST,
            )
