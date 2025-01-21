from channels.routing import URLRouter

from stock_market.routes import stock_ws_routes


stock_market_router = URLRouter(stock_ws_routes)
