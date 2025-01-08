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

        results = []  # QUEUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE

        # 1
        results.append(pool.apply_async(covered_call, args=(option_data,)))

        # # 2
        results.append(pool.apply_async(conversion, args=(option_data,)))

        # # 3
        results.append(pool.apply_async(long_call, args=(option_data,)))

        # # 4
        results.append(pool.apply_async(short_call, args=(option_data,)))

        # # 5
        results.append(pool.apply_async(long_put, args=(option_data,)))

        # # 6
        results.append(pool.apply_async(short_put, args=(option_data,)))

        # # 7
        results.append(pool.apply_async(long_straddle, args=(option_data,)))

        # # 8
        results.append(pool.apply_async(short_straddle, args=(option_data,)))

        # # 9
        results.append(pool.apply_async(bull_call_spread, args=(option_data,)))

        # # 10
        results.append(pool.apply_async(bear_call_spread, args=(option_data,)))

        # # 11
        results.append(pool.apply_async(bull_put_spread, args=(option_data,)))

        # # 12
        results.append(pool.apply_async(bear_put_spread, args=(option_data,)))

        # # 13
        results.append(pool.apply_async(long_strangle, args=(option_data,)))

        # # 14
        results.append(pool.apply_async(short_strangle, args=(option_data,)))

        # # 15
        results.append(pool.apply_async(long_butterfly, args=(option_data,)))

        # # 16
        results.append(pool.apply_async(short_butterfly, args=(option_data,)))

        # # 17
        results.append(pool.apply_async(collar, args=(option_data,)))

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
