import os
import threading

from django.core.files.storage import default_storage
from global_market.tasks import upload_xlsx_relation_task
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from samaneh.settings import BASE_DIR


@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
class UploadRelationAPIView(APIView):
    def post(self, request):
        excel_file = request.FILES.get("relation")

        file_name = excel_file.name
        save_dir = f"{BASE_DIR}/media/uploaded_files/"
        is_dir = os.path.isdir(save_dir)
        if not is_dir:
            os.makedirs(save_dir)
        DEFAULT_PATH = save_dir + file_name

        if excel_file:
            if default_storage.exists(DEFAULT_PATH):
                default_storage.delete(DEFAULT_PATH)
            default_storage.save(DEFAULT_PATH, excel_file)
        else:
            return Response(
                {"message": "مشکل در درخواست!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload_xlsx_relation_task_thread = threading.Thread(
            target=upload_xlsx_relation_task, args=(file_name,)
        )
        upload_xlsx_relation_task_thread.start()

        return Response(
            {
                "message": "درخواست شما دریافت شد. اتمام فرایند افزودن یا به‌روزرسانی اطلاعات زمانبر است."
            },
            status=status.HTTP_200_OK,
        )
