from pathlib import Path

TICKET_APPENDIX_FILES_DIR = (
    f"{Path(__file__).resolve().parent.parent.parent}/media/tickets/"
)

from .ticketing_apiview import (
    TicketingAPIView,
    GetTicketUnitListAPIView,
    GetTicketAppendixAPIView,
    GetTicketDetailAPIView,
    GetTicketFeatureListAPIView,
)
