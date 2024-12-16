from stock_market.serializers import (
    PersonMoneyFlowSerailizer,
    PersonBuyPressureSerailizer,
    PersonBuyValueSerailizer,
    DashboardStockValueChangeSerailizer,
    BuyOrderRatioSerailizer,
    SellOrderRatioSerailizer,
    StockOptionValueChangeDashboardSerailizer,
    StockOptionPriceSpreadSerailizer,
)

STOCK_MARKET_WATCH_INDICES = {
    "money_flow": PersonMoneyFlowSerailizer,
    "buy_pressure": PersonBuyPressureSerailizer,
    "buy_value": PersonBuyValueSerailizer,
    "value_change": DashboardStockValueChangeSerailizer,
    "buy_ratio": BuyOrderRatioSerailizer,
    "sell_ratio": SellOrderRatioSerailizer,
}

OPTION_MARKET_WATCH_INDICES = {
    "call_value_change": StockOptionValueChangeDashboardSerailizer,
    "put_value_change": StockOptionValueChangeDashboardSerailizer,
    "option_price_spread": StockOptionPriceSpreadSerailizer,
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
