import os
from zoneinfo import ZoneInfo

######################################################## CACHE
SIXTY_SECONDS_CACHE = 60  # 60 seconds
FIVE_MINUTES_CACHE = 60 * 5  # 5 minutes
THIRTY_MINUTES_CACHE = 60 * 30  # 30 minutes
SIXTY_MINUTES_CACHE = 60 * 60  # 60 minutes
SIX_HOURS_CACHE = 60 * 60 * 6  # 6 hours

######################################################## REDIS_DBs
KEY_WITH_EX_REDIS_DB = 1  # CORE

######################################################## CORE APP
DASHBOARD_MONGO_DB = "dashboard"
TOTAL_INDEX_DAILY_COLLECTION = "total_index_daily"
UNWEIGHTED_INDEX_DAILY_COLLECTION = "unweighted_index_daily"
BUY_SELL_ORDERS_COLLECTION = "buy_sell_orders"
LAST_CLOSE_PRICE_COLLECTION = "last_close_price"
OPTION_VALUE_ANALYSIS_COLLECTION = "option_value_analysis"
TOP_OPTIONS_COLLECTION = "top_options"
AUTO_MODE = "auto"
MANUAL_MODE = "manual"
MGT_FOR_DAILY_TASKS = 50 * 60  # 50 Minutes

######################################################## ACCOUNT APP
REDIS_SIGNUP_PREFIX = "username_verify_code_"
REDIS_EMAIL_VERIFY_PREFIX = "email_verify_code_"
REDIS_RESET_PASSWORD_PREFIX = "reset_password_code_"
MELIPAYAMAK_OK_RESPONSE = "Ok"
SIGNUP_CODE_EXPIRY = 60 * 5  # 5 Minutes
RESET_PASSWORD_CODE_EXPIRY = SIGNUP_CODE_EXPIRY
EMAIL_VERIFY_CODE_EXPIRY = 60 * 5  # 5 Minutes
SIGNUP_TRY_COUNT_EXPIRY = 60 * 60 * 24  # 24 Hours
CODE_RANGE_MIN = 111111
CODE_RANGE_MAX = 999999
PHONE_PATTERN = r"^09(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])-?[0-9]{3}-?[0-9]{4}$"

######################################################## FUND APP
FUND_MONGO_DB = "fund"
FUND_ALL_DATA_COLLECTION = "all_data"

######################################################## FUTURE APP
FUTURE_MONGO_DB = "future"

######################################################## DOMESTIC APP
DOMESTIC_MONGO_DB = "domestic"

######################################################## GLOBAL APP
GLOBAL_MONGO_DB = "global"

######################################################## OPTIONS APP
OPTION_MONGO_DB = "option"
OPTION_DATA_COLLECTION = "option_data"
OPTION_TRADE_FEE = 0.00103
OPTION_SETTLEMENT_FEE = 0.0005
BASE_EQUITY_BUY_FEE = 0.003712
BASE_EQUITY_SELL_FEE = 0.0088

######################################################## STOCK APP
MARKET_WATCH_REDIS_KEY = "market_watch"
MARKET_WATCH_COLLECTION = "market_watch"
STOCK_MONGO_DB = "stock"
STOCK_NA_ROI = -1000
MARKET_WATCH_TOP_5_LIMIT = 5
STOCK_TOP_500_LIMIT = 500
STOCK_TOP_100_LIMIT = 100
STOCK_NO_ROI_LETTER = "ناموجود"
NO_DAILY_HISTORY = "NDH"
NO_HISTORY_DATE = "NHD"
STOCK_VALUE_CHANGE_DURATION = 30  # DAYS
STOCK_OPTION_STRIKE_DEVIATION = 5  # PERCENT

######################################################## COMMON
# DOMESTIC & GLOBAL MEAN DEVIATION
DASHBOARD_TOP_5_LIMIT = 5
COMMODITY_TOP_200_LIMIT = 200
TEHRAN_TZ = ZoneInfo("Asia/Tehran")

# UNIT CONVERSION
HEZAR_RIAL_TO_MILLION_TOMAN = 10_000
HEZAR_RIAL_TO_BILLION_TOMAN = 10_000_000
RIAL_TO_BILLION_TOMAN = 10_000_000_000
RIAL_TO_MILLION_TOMAN = 10_000_000
TO_MILLION = 1_000_000

# PERSIAN TO ENGLISH NUMBER CONVERTER
PERSIAN_DIGITS = "۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩٠"
ENGLISH_DIGITS = "12345678901234567890"
FA_TO_EN_TRANSLATION_TABLE = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)

# EMAIL
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")

# SMS
PORTFOYAR_SMS_ID = 263013
MELIPAYAMAK_USERNAME = os.environ.get("MELIPAYAMAK_USERNAME")
MELIPAYAMAK_PASSOWRD = os.environ.get("MELIPAYAMAK_PASSOWRD")

# ZARINPAL PAYMENT METHOD CONFIGURATIONS
ZARINPAL_MERCHANTID = os.environ.get("ZARINPAL_MERCHANTID")
ZARINPAL_VERIFY_TRANSACTION_CALLBACKURL = "/api/payment/zarinpal/"
ZP_PAY_REQUEST_URL = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_STARTPAY_URL = "https://www.zarinpal.com/pg/StartPay/"
ZP_REDIRECT_FRONTEND_URL = "/dashboard/profile"
ZP_PAY_VERIFY_URL = "https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"

# ADMIN USER
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_FIRST_NAME = os.environ.get("ADMIN_FIRST_NAME")
ADMIN_LAST_NAME = os.environ.get("ADMIN_LAST_NAME", "!")
