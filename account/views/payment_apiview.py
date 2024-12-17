from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from payment.models import Receipt
from account.serializers import GetReceiptSerailizer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ReceiptAPIView(APIView):
    def get(self, request):
        user = request.user
        receipts = Receipt.objects.filter(user=user).order_by("-updated_at")
        receipts = GetReceiptSerailizer(receipts, many=True)

        return Response(receipts.data, status=status.HTTP_200_OK)
