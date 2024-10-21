from core.utils import task_timing

from . import (
    covered_call,
    long_call,
    # short_call,
    # long_put,
    # short_put,
    # bull_call_spread,
    # bear_call_spread,
    # bull_put_spread,
    # bear_put_spread,
    # long_straddle,
    # short_straddle,
    # long_strangle,
    # short_strangle,
    # long_butterfly,
    # short_butterfly,
    # collar,
    # conversion,
)


def populate_all_strategy(option_data):

    # 1
    covered_call(option_data)

    # # 2
    long_call(option_data)

    # # 3
    # short_call()

    # # 4
    # long_put()

    # # 5
    # short_put()

    # # 6
    # long_straddle()

    # # 7
    # short_straddle()

    # # 8
    # bull_call_spread()

    # # 9
    # bear_call_spread()

    # # 10
    # bull_put_spread()

    # # 11
    # bear_put_spread()

    # # 12
    # long_strangle()

    # # 13
    # short_strangle()

    # # 14
    # long_butterfly()

    # # 15
    # short_butterfly()

    # # 16
    # collar()

    # # 17
    # conversion()

    return
