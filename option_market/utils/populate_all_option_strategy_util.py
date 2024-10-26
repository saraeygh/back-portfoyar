from core.utils import RedisInterface
from core.configs import OPTION_REDIS_DB

from . import (
    get_options,
    covered_call,
    conversion,
    long_call,
    short_call,
    long_put,
    short_put,
    bull_call_spread,
    bear_call_spread,
    bull_put_spread,
    bear_put_spread,
    long_straddle,
    short_straddle,
    long_strangle,
    short_strangle,
    long_butterfly,
    short_butterfly,
    collar,
)


def populate_all_option_strategy():

    option_data = get_options(option_types=["option_data"])

    redis_conn = RedisInterface(db=OPTION_REDIS_DB)

    # 1
    covered_call(option_data, redis_conn)

    # 2
    long_call(option_data, redis_conn)

    # 3
    short_call(option_data, redis_conn)

    # 4
    long_put(option_data, redis_conn)

    # 5
    short_put(option_data, redis_conn)

    # 6
    long_straddle(option_data, redis_conn)

    # 7
    short_straddle(option_data, redis_conn)

    # 8
    bull_call_spread(option_data, redis_conn)

    # 9
    bear_call_spread(option_data, redis_conn)

    # 10
    bull_put_spread(option_data, redis_conn)

    # 11
    bear_put_spread(option_data, redis_conn)

    # 12
    long_strangle(option_data, redis_conn)

    # 13
    short_strangle(option_data, redis_conn)

    # 14
    long_butterfly(option_data, redis_conn)

    # 15
    short_butterfly(option_data, redis_conn)

    # 16
    collar(option_data, redis_conn)

    # 17
    conversion(option_data, redis_conn)

    return
