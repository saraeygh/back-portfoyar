from core.utils import RedisInterface
from core.configs import FUTURE_REDIS_DB

from option_market.utils import (
    covered_call,
    long_call,
    short_call,
    long_put,
    short_put,
    long_straddle,
    short_straddle,
    bull_call_spread,
    bear_call_spread,
    bull_put_spread,
    bear_put_spread,
    long_strangle,
    short_strangle,
    long_butterfly,
    short_butterfly,
    collar,
    conversion,
)


def populate_all_strategy(option_data):

    redis_conn = RedisInterface(db=FUTURE_REDIS_DB)

    # # 1
    covered_call(option_data, redis_conn)

    # # 2
    conversion(option_data, redis_conn)

    # # 3
    long_call(option_data, redis_conn)

    # # 4
    short_call(option_data, redis_conn)

    # # 5
    long_put(option_data, redis_conn)

    # # 6
    short_put(option_data, redis_conn)

    # # 7
    long_straddle(option_data, redis_conn)

    # # 8
    short_straddle(option_data, redis_conn)

    # # 9
    bull_call_spread(option_data, redis_conn)

    # # 10
    bear_call_spread(option_data, redis_conn)

    # # 11
    bull_put_spread(option_data, redis_conn)

    # # 12
    bear_put_spread(option_data, redis_conn)

    # # 13
    long_strangle(option_data, redis_conn)

    # # 14
    short_strangle(option_data, redis_conn)

    # # 15
    long_butterfly(option_data, redis_conn)

    # # 16
    short_butterfly(option_data, redis_conn)

    # # 17
    collar(option_data, redis_conn)
