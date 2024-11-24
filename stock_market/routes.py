from django.urls import path

from stock_market.consumers import MarketWatchConsumer

marketwatch_ws_routes = [
    path("ws/stock-market/stock/", MarketWatchConsumer.as_asgi()),
]
