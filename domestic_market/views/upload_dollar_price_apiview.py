import numpy as np
import pandas as pd
from domestic_market.tasks import upload_dollar_price
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
class UploadDollarPriceAPIView(APIView):
    def post(self, request):
        try:
            dollar_prices_df = pd.read_csv(
                request.FILES.get("dollar"),
                dtype={"date": object, "azad": object, "nima": object},
            )

            dollar_prices_df = dollar_prices_df[
                [
                    "date",
                    "nima",
                    "azad",
                ]
            ]

        except (KeyError, ValueError):
            return Response(
                data={"Error": "فایل ارسالی مطابق الگو نیست"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dollar_prices_df = dollar_prices_df.replace({np.nan: None})
        dollar_prices_list_of_dicts = dollar_prices_df.to_dict(orient="records")

        if dollar_prices_list_of_dicts:
            upload_dollar_price.delay(dollar_prices_list_of_dicts)

            return Response(
                {
                    "message": "درخواست شما دریافت شد. اتمام فرایند افزودن یا به‌روزرسانی اطلاعات زمانبر است، پس از اتمام فرایند، لیست قیمت‌های دلاری که امکان ثبت در دیتابیس را ندارند در قالب یک فایل برای شما ایمیل می‌شود."
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
