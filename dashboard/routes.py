from django.urls import path

from dashboard.consumers import MarketWatchConsumer

marketwatch_ws_routes = [
    path("ws/dashboard/marketwatch/", MarketWatchConsumer.as_asgi()),
]

dashboard_ws_routes = marketwatch_ws_routes
