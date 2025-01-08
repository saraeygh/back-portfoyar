import os
import multiprocessing

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


def populate_all_option_strategy_async():
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    with multiprocessing.Pool(processes=used_cores) as pool:
        option_data = get_options(option_types=["option_data"])
        option_data = option_data[option_data["base_equity_last_price"] > 0]

        STRATEGIES = [
            covered_call,  # 1
            conversion,  # 2
            long_call,  # 3
            short_call,  # 4
            long_put,  # 5
            short_put,  # 6
            bull_call_spread,  # 7
            bear_call_spread,  # 8
            bull_put_spread,  # 9
            bear_put_spread,  # 10
            long_straddle,  # 11
            short_straddle,  # 12
            long_strangle,  # 13
            short_strangle,  # 14
            long_butterfly,  # 15
            short_butterfly,  # 16
            collar,  # 17
        ]
        for strategy in STRATEGIES:
            pool.apply_async(strategy, args=(option_data,))

        pool.close()
        pool.join()


def populate_all_option_strategy_sync():
    option_data = get_options(option_types=["option_data"])
    option_data = option_data[option_data["base_equity_last_price"] > 0]

    redis_conn = RedisInterface(db=OPTION_REDIS_DB)

    # 1
    covered_call(option_data, redis_conn)

    # 2
    conversion(option_data, redis_conn)

    # 3
    long_call(option_data, redis_conn)

    # 4
    short_call(option_data, redis_conn)

    # 5
    long_put(option_data, redis_conn)

    # 6
    short_put(option_data, redis_conn)

    # 7
    long_straddle(option_data, redis_conn)

    # 8
    short_straddle(option_data, redis_conn)

    # 9
    bull_call_spread(option_data, redis_conn)

    # 10
    bear_call_spread(option_data, redis_conn)

    # 11
    bull_put_spread(option_data, redis_conn)

    # 12
    bear_put_spread(option_data, redis_conn)

    # 13
    long_strangle(option_data, redis_conn)

    # 14
    short_strangle(option_data, redis_conn)

    # 15
    long_butterfly(option_data, redis_conn)

    # 16
    short_butterfly(option_data, redis_conn)

    # 17
    collar(option_data, redis_conn)
