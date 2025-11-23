import os
import multiprocessing

from core.configs import OPTION_MONGO_DB

from . import (
    covered_call,
    conversion,
    married_put,
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

STRATEGIES = [
    covered_call,  # 1
    conversion,  # 2
    married_put,  # 3
    long_call,  # 4
    short_call,  # 5
    long_put,  # 6
    short_put,  # 7
    bull_call_spread,  # 8
    bear_call_spread,  # 9
    bull_put_spread,  # 10
    bear_put_spread,  # 11
    long_straddle,  # 12
    short_straddle,  # 13
    long_strangle,  # 14
    short_strangle,  # 15
    long_butterfly,  # 16
    short_butterfly,  # 17
    collar,  # 18
]


def populate_all_option_strategy_sync(option_data):

    for strategy in STRATEGIES:
        strategy(option_data, OPTION_MONGO_DB)


def populate_all_option_strategy_async(option_data):
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    with multiprocessing.Pool(processes=used_cores) as pool:
        for strategy in STRATEGIES:
            pool.apply_async(strategy, args=(option_data, OPTION_MONGO_DB))

        pool.close()
        pool.join()
