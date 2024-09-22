from django.db.models import Q
from django.shortcuts import get_object_or_404
from core.utils import RedisInterface
from option_market.models import Strategy
from favorite.models import OptionsFavoriteSymbol
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class OptionsFavoriteSymbolAPIView(APIView):
    def get(self, request, collection_key):
        strategy = get_object_or_404(Strategy, collection_key=collection_key)

        favorite_symbols = list(
            request.user.options_favorite_symbols.filter(strategy=strategy).values_list(
                "symbol", flat=True
            )
        )

        redis_conn = RedisInterface(db=3)
        options_list = redis_conn.get_list_of_dicts(list_key=collection_key)

        favorite_symbols_options = [
            option for option in options_list if option["symbol"] in favorite_symbols
        ]

        return Response(data=favorite_symbols_options, status=status.HTTP_200_OK)

    def post(self, request, collection_key):
        user = request.user
        strategy = get_object_or_404(Strategy, collection_key=collection_key)
        symbols = request.data.get("symbols")

        bulk_favorite = []
        if symbols:
            for symbol in symbols:
                if OptionsFavoriteSymbol.objects.filter(
                    Q(user=request.user) & Q(strategy=strategy) & Q(symbol=symbol)
                ).exists():
                    continue

                favorite_symbol = {
                    "user": user,
                    "strategy": strategy,
                    "symbol": symbol,
                }
                new_favorite = OptionsFavoriteSymbol(**favorite_symbol)
                bulk_favorite.append(new_favorite)

            OptionsFavoriteSymbol.objects.bulk_create(objs=bulk_favorite)

        return Response(
            {"message": "نماد مورد علاقه با موفقیت اضافه شد."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, collection_key, symbol):
        strategy = get_object_or_404(Strategy, collection_key=collection_key)

        favorite = get_object_or_404(
            OptionsFavoriteSymbol,
            Q(user=request.user) & Q(strategy=strategy) & Q(symbol=symbol),
        )

        favorite.delete()

        return Response(
            {"message": "نماد مورد علاقه با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT,
        )
