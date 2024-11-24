from django.shortcuts import get_object_or_404
from favorite.models import StockFavoriteROIGroup, ROIGroupInstrument
from favorite.utils import get_instrument_roi
from stock_market.serializers import FavoriteGroupMarketROISerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockFavoriteROIInstrumentAPIView(APIView):
    def get(self, request, group_id):
        group = get_object_or_404(StockFavoriteROIGroup, id=group_id, user=request.user)
        instruments = ROIGroupInstrument.objects.filter(group=group.id)
        if instruments.count() < 1:
            return Response(data=[], status=status.HTTP_200_OK)

        instrument_roi = get_instrument_roi(instruments)
        instrument_roi = FavoriteGroupMarketROISerailizer(
            instrument_roi, many=True, context={"group_id": group_id}
        )

        return Response(data=instrument_roi.data, status=status.HTTP_200_OK)

    def delete(self, request, group_id, symbol):
        group = get_object_or_404(StockFavoriteROIGroup, id=group_id, user=request.user)
        instrument = ROIGroupInstrument.objects.filter(group=group).filter(
            instrument__symbol=symbol
        )
        if instrument.exists():
            instrument.delete()
            return Response({"message": "با موفقیت حذف شد."}, status=status.HTTP_200_OK)

        return Response({"message": "این نماد وجود ندارد."}, status=status.HTTP_200_OK)
