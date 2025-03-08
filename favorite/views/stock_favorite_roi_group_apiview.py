from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from favorite.models import StockFavoriteROIGroup
from favorite.utils import get_group_roi
from stock_market.serializers import IndustryROISerailizer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockFavoriteROIGroupAPIView(APIView):
    def get(self, request):
        user = request.user
        favorite_roi_groups = user.favorite_roi_groups.all()
        if favorite_roi_groups.count() < 1:
            return Response(data=[], status=status.HTTP_200_OK)

        group_roi = get_group_roi(favorite_roi_groups)
        group_roi = IndustryROISerailizer(group_roi, many=True)

        return Response(data=group_roi.data, status=status.HTTP_200_OK)

    def post(self, request):
        group_name = request.data.get("name")
        group_name = group_name.strip()
        if group_name == "" or group_name is None:
            return Response(
                {"message": "درخواست نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
            )
        new_group = StockFavoriteROIGroup(user=request.user, name=group_name)
        new_group.save()
        return Response({"message": "با موفقیت افزوده شد"}, status=status.HTTP_200_OK)

    def patch(self, request):
        group_id = request.data.get("group_id")
        group_name = request.data.get("name")

        group = get_object_or_404(StockFavoriteROIGroup, id=group_id, user=request.user)
        group.name = group_name
        group.save()

        return Response({"message": "با موفقیت ویرایش شد"}, status=status.HTTP_200_OK)

    def delete(self, request, favorite_id):
        group = get_object_or_404(
            StockFavoriteROIGroup, id=favorite_id, user=request.user
        )
        group.delete()

        return Response({"message": "با موفقیت پاک شد"}, status=status.HTTP_200_OK)
