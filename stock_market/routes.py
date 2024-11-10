from django.urls import path
from stock_market.consumers import MarketWatchConsumer

stock_ws_routes = [
    path("ws/stock/marketwatch/", MarketWatchConsumer.as_asgi()),
]
