from .dashboard_menu_apiview import IndustrialGroupsAPIView, PaperTypesAPIView
from .dollar_price_apiview import DollarPriceAPIView
from .buy_sell_value_apiview import BuySellValueAPIView
from .last_close_price_apiview import LastClosePriceAPIView
from .total_index_daily_apiview import TotalIndexDailyAPIView
from .unweighted_index_daily_apiview import UnweightedIndexDailyAPIView
from .option_value_analysis_apiview import (
    OptionValueAPIView,
    CallValueAPIView,
    PutValueAPIView,
    CallToPutAPIView,
    OptionToMarketAPIView,
)
from .domestic_dashboard_apiview import DomesticMeanDeviationAPIView
from .global_dashboard_apiview import GlobalMeanDeviationAPIView
