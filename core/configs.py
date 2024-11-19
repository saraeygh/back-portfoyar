import os

######################################################## CACHE
SIXTY_SECONDS_CACHE = 60  # 60 seconds
FIVE_MINUTES_CACHE = 60 * 5  # 5 minutes
THIRTY_MINUTES_CACHE = 60 * 30  # 30 minutes
SIXTY_MINUTES_CACHE = 60 * 60  # 60 minutes
SIX_HOURS_CACHE = 60 * 60 * 6  # 6 hours


######################################################## REDIS_DBs
KEY_WITH_EX_REDIS_DB = 1  # CORE
OPTION_REDIS_DB = 3  # FUTURE
FUTURE_REDIS_DB = 4  # FUTURE
STOCK_REDIS_DB = 5  # STOCK
USER_AGENTS_REDIS_DB = 13  # CORE
USER_STATS_REDIS_DB = 14  # CORE
ONLINE_USERS_REDIS_DB = 15  # CORE


######################################################## CORE APP
STATS_MONGO_DB = "stats"
DASHBOARD_MONGO_DB = "dashboard"
BUY_SELL_ORDERS_COLLECTION = "buy_sell_orders"
AUTO_MODE = "auto"
MANUAL_MODE = "manual"


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


######################################################## DOMESTIC APP
DOMESTIC_MONGO_DB = "domestic"


######################################################## GLOBAL APP
GLOBAL_MONGO_DB = "global"


######################################################## OPTIONS APP
OPTION_MONGO_DB = "option"
OPTION_TRADE_FEE = 0.00103
OPTION_LIQUIDATION_SETTLEMENT_FEE = 0.0005
OPTION_PHYSICAL_SETTLEMENT_FEE = 0.0005
BASE_EQUITY_BUY_FEE = 0.003712
BASE_EQUITY_SELL_FEE = 0.0088

######################################################## STOCK APP
MARKET_WATCH_REDIS_KEY = "market_watch"
STOCK_MONGO_DB = "stock"
STOCK_NA_ROI = -1000
STOCK_TOP_500_LIMIT = 500
STOCK_TOP_100_LIMIT = 100
STOCK_NO_ROI_LETTER = "ناموجود"
NO_DAILY_HISTORY = "NDH"
NO_HISTORY_DATE = "NHD"
STOCK_VALUE_CHANGE_DURATION = 30  # DAYS
STOCK_OPTION_STRIKE_DEVIATION = 5  # PERCENT
DEFAULT_RECOMMENDATION_CONFIG_NAME = "portfoyar_admin_default_recommendation_configs"
MARKET_WATCH_URL = (
    "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch?"
    "market=0&"
    "industrialGroup=&"
    "paperTypes[0]=1&"
    "paperTypes[1]=2&"
    "paperTypes[2]=3&"
    "paperTypes[3]=4&"
    "paperTypes[4]=5&"
    "paperTypes[5]=6&"
    "paperTypes[6]=7&"
    "paperTypes[7]=8&"
    "paperTypes[8]=9&"
    "showTraded=true&"
    "withBestLimits=true&"
    "hEven=0&"
    "RefID=0"
)
CLIENT_TYPE_URL = "https://cdn.tsetmc.com/api/ClientType/GetClientTypeAll"

######################################################## COMMON
# DOMESTIC & GLOBAL MEAN DEVIATION
COMMODITY_TOP_200_LIMIT = 200

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
EMAIL_HOST = os.environ.setdefault("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = os.environ.setdefault("EMAIL_PORT", "587")
EMAIL_HOST_USER = os.environ.setdefault("EMAIL_HOST_USER", "armansmtptest@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.setdefault(
    "EMAIL_HOST_PASSWORD", "gaux sxiy zhyf qhdx"
)
EMAIL_TO = os.environ.setdefault("EMAIL_TO", "saraey.gholamreza@gmail.com")

# SMS
PORTFOYAR_SMS_ID = 263013
MELIPAYAMAK_USERNAME = os.environ.setdefault("MELIPAYAMAK_USERNAME", "09102188113")
MELIPAYAMAK_PASSOWRD = os.environ.setdefault("MELIPAYAMAK_PASSOWRD", "TL5OC")
