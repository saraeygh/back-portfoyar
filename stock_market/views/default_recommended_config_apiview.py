from stock_market.utils import get_default_recomm_configs, get_recommendation_config
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetRecommendedConfigAPIView(APIView):
    def get(self, request):

        config = get_recommendation_config(user=request.user)

        related_objects = config.get_related_objects_as_dict()
        config = get_default_recomm_configs(related_objects)

        return Response(config, status=status.HTTP_200_OK)
