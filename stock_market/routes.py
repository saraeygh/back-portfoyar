from django.urls import path
from channels.routing import URLRouter

from stock_market.consumers import MarketWatchConsumer

stock_ws_routes = [
    path("marketwatch", MarketWatchConsumer.as_asgi()),
]


stock_market_router = URLRouter(stock_ws_routes)
