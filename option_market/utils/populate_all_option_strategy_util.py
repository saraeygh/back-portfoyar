import multiprocessing
import time

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
    import time

    start_time = time.perf_counter()  # Start high-resolution timer

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

    end_time = time.perf_counter()  # Stop high-resolution timer
    duration = end_time - start_time

    print(f"SYNC completed in {duration:.2f} seconds.")


def populate_all_option_strategy_mp():

    start_time = time.perf_counter()
    ################################

    option_data = get_options(option_types=["option_data"])
    option_data = option_data[option_data["base_equity_last_price"] > 0]

    redis_conn = RedisInterface(db=OPTION_REDIS_DB)

    with multiprocessing.Pool(processes=4) as pool:
        # 1
        pool.apply_async(covered_call, args=(option_data, redis_conn))

        # 2
        pool.apply_async(conversion, args=(option_data, redis_conn))

        # 3
        pool.apply_async(long_call, args=(option_data, redis_conn))

        # 4
        pool.apply_async(short_call, args=(option_data, redis_conn))

        # 5
        pool.apply_async(long_put, args=(option_data, redis_conn))

        # 6
        pool.apply_async(short_put, args=(option_data, redis_conn))

        # 7
        pool.apply_async(long_straddle, args=(option_data, redis_conn))

        # 8
        pool.apply_async(short_straddle, args=(option_data, redis_conn))

        # 9
        pool.apply_async(bull_call_spread, args=(option_data, redis_conn))

        # 10
        pool.apply_async(bear_call_spread, args=(option_data, redis_conn))

        # 11
        pool.apply_async(bull_put_spread, args=(option_data, redis_conn))

        # 12
        pool.apply_async(bear_put_spread, args=(option_data, redis_conn))

        # 13
        pool.apply_async(long_strangle, args=(option_data, redis_conn))

        # 14
        pool.apply_async(short_strangle, args=(option_data, redis_conn))

        # 15
        pool.apply_async(long_butterfly, args=(option_data, redis_conn))

        # 16
        pool.apply_async(short_butterfly, args=(option_data, redis_conn))

        # 17
        pool.apply_async(collar, args=(option_data, redis_conn))

        pool.close()
        pool.join()

    end_time = time.perf_counter()
    duration = end_time - start_time
    ################################

    print(f"ASYNC completed in {duration:.2f} seconds.")
