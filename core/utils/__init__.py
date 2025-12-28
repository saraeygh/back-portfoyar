from .get_http_response_util import get_http_response
from .redis_interface_util import RedisInterface
from .run_main_task_util import print_task_info, run_main_task
from .mongodb_interface_util import MongodbInterface
from .send_upload_error_file_email_util import send_upload_error_file_email
from .get_set_json_cache_util import set_json_cache, get_cache_as_json
from .clear_redis_cache_util import clear_redis_cache
from .add_df_index_as_id_util import add_index_as_id
from .replace_arabic_letters_util import (
    replace_arabic_letters,
    replace_arabic_letters_pd,
    replace_all_arabic_letters_in_db,
)
from .populate_strategy_option_util import populate_strategy_option, STRATEGIES
from .create_admin_user_util import create_admin_user
from .create_default_feature_toggle_util import (
    create_default_feature_toggle,
    MARKET_STATE,
    MONTHLY_INTEREST_RATE,
    SEND_SIGNUP_SMS,
    DAILY_SIGNUP_TRY_LIMITATION,
    SEND_CHANGE_USERNAME_SMS,
    SEND_RESET_PASSWORD_SMS,
    NEW_USER_FREE_DURATION,
)
from .create_profile_for_users_with_no_profile_util import (
    create_profile_for_users_with_no_profile,
)
from .get_deviation_percent_util import get_deviation_percent
from .persian_numbers_to_english_util import persian_numbers_to_english
from .was_market_open_today_util import is_market_open_today
from .get_relative_datetime_util import get_relative_datetime

TABLE_COLS_QP = "table"
ALL_TABLE_COLS = "all"
SUMMARY_TABLE_COLS = "summary"

CLIENT_TYPE_URL = "https://cdn.tsetmc.com/api/ClientType/GetClientTypeAll"
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


TSETMC_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "cdn.tsetmc.com",
    "Origin": "https://main.tsetmc.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
}
