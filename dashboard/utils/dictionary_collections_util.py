from stock_market.serializers import (
    PersonMoneyFlowSerailizer,
    PersonBuyPressureSerailizer,
    PersonBuyValueSerailizer,
    StockValueChangeSerailizer,
    BuyOrderRatioSerailizer,
    SellOrderRatioSerailizer,
)

MARKET_WATCH_INDICES = {
    "money_flow": PersonMoneyFlowSerailizer,
    "buy_pressure": PersonBuyPressureSerailizer,
    "buy_value": PersonBuyValueSerailizer,
    "value_change": StockValueChangeSerailizer,
    "buy_ratio": BuyOrderRatioSerailizer,
    "sell_ratio": SellOrderRatioSerailizer,
}

TSE_ORDER_BOOK = {
    "n": "row",
    # BUY
    "zmd": "buy_count",
    "qmd": "buy_volume",
    "pmd": "buy_price",
    # SELL
    "zmo": "sell_count",
    "qmo": "sell_volume",
    "pmo": "sell_price",
}
