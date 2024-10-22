from . import (
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

    # 1
    covered_call(option_data)

    # # 2
    long_call(option_data)

    # # 3
    short_call(option_data)

    # # 4
    long_put(option_data)

    # # 5
    short_put(option_data)

    # # 6
    long_straddle(option_data)

    # # 7
    short_straddle(option_data)

    # # 8
    bull_call_spread(option_data)

    # # 9
    bear_call_spread(option_data)

    # # 10
    bull_put_spread(option_data)

    # # 11
    bear_put_spread(option_data)

    # # 12
    long_strangle(option_data)

    # # 13
    short_strangle(option_data)

    # # 14
    long_butterfly(option_data)

    # # 15
    short_butterfly(option_data)

    # # 16
    collar(option_data)

    # # 17
    conversion(option_data)

    return
