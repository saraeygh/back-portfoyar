import os
import multiprocessing

from core.configs import FUTURE_MONGO_DB

from option_market.utils import (
    covered_call,
    conversion,
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
)


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


def populate_all_strategy_sync(option_data):

    for strategy in STRATEGIES:
        strategy(option_data, FUTURE_MONGO_DB)


def populate_all_strategy_async(option_data):
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    with multiprocessing.Pool(processes=used_cores) as pool:
        for strategy in STRATEGIES:
            pool.apply_async(strategy, args=(option_data, FUTURE_MONGO_DB))

        pool.close()
        pool.join()
