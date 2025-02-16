from django.urls import path

from fund.views import CheckUploadDataAPIView

fund_upload_urls = [
    path("check-upload-data", CheckUploadDataAPIView.as_view()),
]


urlpatterns = fund_upload_urls
