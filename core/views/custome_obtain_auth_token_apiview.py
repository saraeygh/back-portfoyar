from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken import views
from rest_framework.response import Response


class CustomeObtainAuthToken(views.ObtainAuthToken):
    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        token = response.data.get("token")

        if token:
            data = {"token": token}
            username = request.data.get("username")
            user = get_object_or_404(User, username=username)
            full_name = user.get_full_name()
            if full_name is None or full_name == "":
                full_name = username
            data["full_name"] = full_name

            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"detail": "مشکلی رخ داده است"},
                status=status.HTTP_400_BAD_REQUEST,
            )
