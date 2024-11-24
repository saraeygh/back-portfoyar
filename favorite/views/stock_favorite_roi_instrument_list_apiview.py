import pandas as pd
from django.shortcuts import get_object_or_404
from core.utils import replace_arabic_letters_pd

from favorite.models import StockFavoriteROIGroup, ROIGroupInstrument
from stock_market.models import StockInstrument
from favorite.serializers import StockFavoriteInstrumentListSerializer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockFavoriteROIInstrumentListAPIView(APIView):
    def get(self, request):
        instruments = StockInstrument.objects.filter(paper_type__in=[1, 2]).values(
            "id", "symbol", "name"
        )
        instruments = pd.DataFrame(instruments)
        instruments = instruments[~instruments["symbol"].str.contains(r"\d")]
        instruments["name"] = instruments.apply(
            replace_arabic_letters_pd, axis=1, args=("name",)
        )
        instruments["symbol"] = instruments.apply(
            replace_arabic_letters_pd, axis=1, args=("symbol",)
        )
        instruments = instruments.to_dict(orient="records")
        instruments = StockFavoriteInstrumentListSerializer(instruments, many=True)

        return Response(data=instruments.data, status=status.HTTP_200_OK)

    def post(self, request):
        group_id = request.data.get("group_id")
        instrument_id = request.data.get("instrument_id")

        group = get_object_or_404(StockFavoriteROIGroup, id=group_id, user=request.user)
        instrument = get_object_or_404(StockInstrument, id=instrument_id)

        exists = ROIGroupInstrument.objects.filter(
            group=group, instrument=instrument
        ).exists()
        if exists:
            return Response(
                {"message": "قبلاً اضافه شده است"}, status=status.HTTP_400_BAD_REQUEST
            )

        new_instrument = ROIGroupInstrument(group=group, instrument=instrument)
        new_instrument.save()

        return Response({"message": "با موفقیت ساخته شد"}, status=status.HTTP_200_OK)
