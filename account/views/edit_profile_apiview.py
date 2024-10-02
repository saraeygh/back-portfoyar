from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


def update_user_first_name(user, first_name):
    if isinstance(first_name, str):
        user.first_name = first_name
        user.save()
        return True

    return False


def update_user_last_name(user, last_name):
    if isinstance(last_name, str):
        user.last_name = last_name
        user.save()
        return True

    return False


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ProfileAPIView(APIView):
    def get(self, request):
        profile = {
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

        return Response(profile, status=status.HTTP_200_OK)

    def patch(self, request):
        response = {}
        user = request.user

        if not update_user_first_name(user, request.data.get("first_name")):
            response["first_name"] = "نام اشتباه است"
        if not update_user_last_name(user, request.data.get("last_name")):
            response["last_name"] = "نام خانوادگی اشتباه است"

        if response:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)
