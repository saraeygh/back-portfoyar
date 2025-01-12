from django.urls import path

from support.views import (
    TicketingAPIView,
    GetTicketUnitListAPIView,
    GetTicketAppendixAPIView,
    GetTicketDetailAPIView,
    GetTicketFeatureListAPIView,
)


ticket_urls = [
    path("ticket/units", GetTicketUnitListAPIView.as_view()),
    path("ticket/features", GetTicketFeatureListAPIView.as_view()),
    path("ticket", TicketingAPIView.as_view()),
    path("ticket/<int:ticket_id>", GetTicketDetailAPIView.as_view()),
    path("appendix/<str:file_name>", GetTicketAppendixAPIView.as_view()),
]

urlpatterns = ticket_urls
