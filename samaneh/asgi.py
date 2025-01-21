"""
ASGI config for samaneh project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

# from core.test_consumer import test_router
from stock_market.router import stock_market_router


application = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path(
                            "ws/",
                            URLRouter(
                                [
                                    path("stock/", stock_market_router),
                                    # path("test", test_router),
                                ]
                            ),
                        ),
                    ]
                )
            )
        ),
    }
)
