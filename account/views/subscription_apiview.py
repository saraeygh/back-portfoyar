from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from account.models import Subscription
from account.serializers import GetSubscriptionSerailizer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SubscriptionAPIView(APIView):
    def get(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(
            user=user, is_enabled=True
        ).order_by("-end_at")
        subscriptions = GetSubscriptionSerailizer(subscriptions, many=True)
        return Response(subscriptions.data, status=status.HTTP_200_OK)
