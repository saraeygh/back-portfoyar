import pandas as pd
import numpy as np

EXTEND_POSITIVE_RANGE_COEFFICIENT = 2


def get_distinc_end_date_options(option_data: pd.DataFrame):
    if option_data.empty:
        return pd.DataFrame()

    grouped_options = list()
    for _, base_equity_group in option_data.groupby("base_equity_symbol"):
        for _, end_date_group in base_equity_group.groupby("end_date"):
            end_date_group.sort_values(by="strike_price", inplace=True)
            grouped_options.append(end_date_group)

    return grouped_options


def get_profit_range(
    _type: str = "call",
    buy_or_sell: str = "buy",
    strike: float = 1000,
    premium: float = 100,
    price_range: np.arange = np.arange(3000),
):
    if _type == "call" and buy_or_sell == "buy":
        result = np.where(
            price_range < strike, -premium, price_range - premium - strike
        )
    elif _type == "call" and buy_or_sell == "sell":
        result = np.where(
            price_range < strike, -1 * (-premium), -1 * (price_range - premium - strike)
        )
    elif _type == "put" and buy_or_sell == "buy":
        result = np.where(
            price_range < strike, strike - premium - price_range, -premium
        )
    elif _type == "put" and buy_or_sell == "sell":
        result = np.where(
            price_range < strike, -1 * (strike - premium - price_range), -1 * (-premium)
        )
    else:
        return None

    return result


class CartesianProduct:

    def __init__(
        self, dataframe: pd.DataFrame, iterations: int = 1, include_equal: bool = False
    ):
        self.dataframe = dataframe
        self.iterations = iterations
        self.include_equal = include_equal

    def __get_cartesian_product(
        self, dataframe_1: pd.DataFrame, dataframe_2: pd.DataFrame, iter_number: int
    ):
        prev_col = f"strike_price_{iter_number}"
        next_col = "strike_price"
        new_col = f"strike_price_{iter_number + 1}"

        new_rows = []
        for _, row in dataframe_1.iterrows():
            unique_prices = dataframe_2[next_col].unique()

            for price in unique_prices:
                if self.include_equal and price > row[prev_col]:
                    continue
                elif not self.include_equal and price >= row[prev_col]:
                    continue
                else:
                    new_row = row.copy()
                    new_row[new_col] = price
                    new_rows.append(new_row)

        new_df = pd.DataFrame(new_rows)
        return new_df

    def get_cartesian_product(self):
        dataframe = self.dataframe.copy(deep=True)
        dataframe["strike_price_0"] = dataframe["strike_price"]
        self.dataframe = dataframe.copy(deep=True)

        result_list = []
        for iter_number in range(self.iterations):
            dataframe = self.__get_cartesian_product(
                dataframe_1=dataframe,
                dataframe_2=self.dataframe,
                iter_number=iter_number,
            )

            if not dataframe.empty:
                result_list.append(dataframe)

        return result_list


class AddOption:
    def __init__(self) -> None:
        self.__option_list = []

    @property
    def get_option_list(self):
        return self.__option_list

    def add_call_buy(self, strike: float, premium: float):
        new_option = {
            "type": "call",
            "buy_or_sell": "buy",
            "strike": strike,
            "premium": premium,
        }

        self.__option_list.append(new_option)

        return self.get_option_list

    def add_call_sell(self, strike: float, premium: float):
        new_option = {
            "type": "call",
            "buy_or_sell": "sell",
            "strike": strike,
            "premium": premium,
        }

        self.__option_list.append(new_option)

        return self.get_option_list

    def add_put_buy(self, strike: float, premium: float):
        new_option = {
            "type": "put",
            "buy_or_sell": "buy",
            "strike": strike,
            "premium": premium,
        }

        self.__option_list.append(new_option)

        return self.get_option_list

    def add_put_sell(self, strike: float, premium: float):
        new_option = {
            "type": "put",
            "buy_or_sell": "sell",
            "strike": strike,
            "premium": premium,
        }

        self.__option_list.append(new_option)

        return self.get_option_list


STRATEGY_NAME_LIST = []


class Strategy:
    RANGE_LIMIT = 200
    INFINITE_PROFIT = 1
    INFINITE_LOSS = -1
    FINITE_PROFIT_LOSS = 0
    STRATEGY_NAME_LIST = []

    def __init__(
        self,
        range_min: float = 50,
        range_max: float = 50,
        option_list: list[dict] = [],
        name: str = "",
    ):
        self.range_min = range_min
        self.range_max = range_max
        self.option_list = option_list
        self.slop = []
        STRATEGY_NAME_LIST.append(name)

    def get_price_range(self):
        if not self.option_list:
            return np.arange(-1 * self.range_min, abs(self.range_max))

        unique_strikes = list(map(lambda x: x["strike"], self.option_list))
        unique_strikes = sorted(list(set(unique_strikes)))

        price_range_min = int(min(unique_strikes) - self.range_min)
        price_range_max = int(max(unique_strikes) + self.range_max)

        price_range_step = (price_range_max - price_range_min) // self.RANGE_LIMIT
        price_range = list(range(price_range_min, price_range_max, price_range_step))
        price_range = sorted(price_range + unique_strikes)
        price_range = np.array(price_range)

        return price_range

    def __get_unique_strikes(self):
        unique_strikes = list(map(lambda x: x["strike"], self.option_list))
        unique_strikes = sorted(list(set(unique_strikes)))

        return unique_strikes

    def __get_intervals(self, intervals_count, unique_strikes):
        intervals = []
        for i in range(1, intervals_count - 1):
            intervals.append((unique_strikes[i - 1], unique_strikes[i]))
        intervals.append((unique_strikes[-1], np.inf))
        intervals.insert(0, (-np.inf, unique_strikes[0]))

        return intervals

    def get_slope(self):
        unique_strikes = self.__get_unique_strikes()
        intervals_count = len(unique_strikes) + 1

        intervals = self.__get_intervals(
            intervals_count=intervals_count, unique_strikes=unique_strikes
        )

        slopes = []
        for option in self.option_list:
            slope = [0] * intervals_count

            if option["type"] == "call":
                for i, period in enumerate(intervals):
                    if option["strike"] < period[1] and option["buy_or_sell"] == "buy":
                        slope[i] = 1
                    if option["strike"] < period[1] and option["buy_or_sell"] == "sell":
                        slope[i] = -1

            if option["type"] == "put":
                for i, period in enumerate(intervals):
                    if option["strike"] > period[0] and option["buy_or_sell"] == "buy":
                        slope[i] = -1
                    if option["strike"] > period[0] and option["buy_or_sell"] == "sell":
                        slope[i] = 1

            slopes.append(np.array(slope))

        result = sum(slopes)

        return list(zip(intervals, result))

    def get_profit_loss(self):

        slopes = self.get_slope()
        price_up_slope = slopes[-1][1]
        price_down_slope = slopes[0][1]

        profit_loss = {}
        if price_up_slope > 0:
            profit_loss["price_up"] = self.INFINITE_PROFIT
        elif price_up_slope < 0:
            profit_loss["price_up"] = self.INFINITE_LOSS
        else:
            profit_loss["price_up"] = self.FINITE_PROFIT_LOSS

        if price_down_slope > 0:
            profit_loss["price_down"] = self.INFINITE_LOSS
        elif price_down_slope < 0:
            profit_loss["price_down"] = self.INFINITE_PROFIT
        else:
            profit_loss["price_down"] = self.FINITE_PROFIT_LOSS

        return profit_loss

    def is_profit_unlimited(self):
        profit_loss = self.get_profit_loss()
        if (
            profit_loss["price_up"] == self.INFINITE_PROFIT
            and profit_loss["price_down"] == self.INFINITE_PROFIT
        ):
            return True
        return False

    def is_loss_unlimited(self):
        profit_loss = self.get_profit_loss()
        if (
            profit_loss["price_up"] == self.INFINITE_LOSS
            and profit_loss["price_down"] == self.INFINITE_LOSS
        ):
            return True
        return False

    def is_limited(self):
        profit_loss = self.get_profit_loss()
        if (
            profit_loss["price_up"] == self.FINITE_PROFIT_LOSS
            and profit_loss["price_down"] == self.FINITE_PROFIT_LOSS
        ):
            return True
        return False

    def __get_strike_value(self):
        strikes = self.__get_unique_strikes()
        slopes = self.get_slope()

        result = {}
        last_result = sum(
            list(
                map(
                    lambda x: (
                        x["premium"]
                        if x["buy_or_sell"] == "sell"
                        else -1 * x["premium"]
                    ),
                    self.option_list,
                )
            )
        )
        for i, strike in enumerate(strikes):
            if i == 0:
                result[strike] = last_result
            else:
                range_delta = slopes[i][0][1] - slopes[i][0][0]
                range_slope = slopes[i][1]
                strike_result = last_result + (range_slope * range_delta)
                last_result = strike_result
                result[strikes[i]] = float(last_result)

        return result

    def __get_intersection(self, y_1, x_2, y_2, m):
        x_1 = x_2 - ((y_2 - y_1) / m)

        return float(x_1)

    def __get_coordinate_range(self, strike_values, slope, strike_position):
        strike = slope[0][strike_position]
        strike_value = strike_values.get(strike)
        range_slop = slope[1]

        return strike, strike_value, range_slop

    def __get_left_range_y(self, x_1, x_2, y_2, m):
        y_1 = y_2 - (m * (x_2 - x_1))

        return float(y_1)

    def __get_right_range_y(self, x_1, y_1, x_2, m):
        y_2 = y_1 + (m * (x_2 - x_1))

        return float(y_2)

    def get_break_even(self):
        strike_values = self.__get_strike_value()
        slopes = self.get_slope()

        break_even_dict = {}
        for i, slope in enumerate(slopes):
            if i == 0:
                strike, strike_value, range_slop = self.__get_coordinate_range(
                    strike_values=strike_values, slope=slope, strike_position=1
                )
                if strike_value * range_slop > 0:
                    break_even_dict[slope[0]] = self.__get_intersection(
                        y_1=0, x_2=strike, y_2=strike_value, m=range_slop
                    )
            elif i == len(slopes) - 1:
                strike, strike_value, range_slop = self.__get_coordinate_range(
                    strike_values=strike_values, slope=slope, strike_position=0
                )
                if strike_value * range_slop < 0:
                    break_even_dict[slope[0]] = self.__get_intersection(
                        y_1=0, x_2=strike, y_2=strike_value, m=range_slop
                    )

            else:
                left_strike, left_strike_value, range_slop = (
                    self.__get_coordinate_range(
                        strike_values=strike_values, slope=slope, strike_position=0
                    )
                )
                right_strike, right_strike_value, range_slop = (
                    self.__get_coordinate_range(
                        strike_values=strike_values, slope=slope, strike_position=1
                    )
                )

                if left_strike_value * right_strike_value < 0:
                    break_even_dict[slope[0]] = self.__get_intersection(
                        y_1=0, x_2=left_strike, y_2=left_strike_value, m=range_slop
                    )

                elif left_strike_value * right_strike_value == 0 and (
                    left_strike_value != 0 or right_strike_value != 0
                ):
                    if (
                        left_strike_value == 0
                        and slopes[i - 1][1] != 0
                        and (slopes[i - 1][1] * slope[1] > 0)
                    ):
                        break_even_dict[slope[0]] = left_strike
                    elif (
                        right_strike_value == 0
                        and slopes[i + 1][1] != 0
                        and (slopes[i + 1][1] * slope[1] > 0)
                    ):
                        break_even_dict[slope[0]] = right_strike

        return break_even_dict

    def get_profit_loss_ranges(self):
        break_evens = self.get_break_even()
        if not break_evens:
            return [(-np.inf, np.inf), "negative"]

        break_points = sorted(
            list(set(break_evens.values()) | set(self.__get_unique_strikes()))
        )
        intervals_count = len(break_points) + 1
        intervals = self.__get_intervals(
            intervals_count=intervals_count, unique_strikes=break_points
        )

        break_point_values = self.__get_strike_value()
        for break_point in break_points:
            if break_point not in break_point_values:
                break_point_values[break_point] = 0

        slopes = self.get_slope()
        result = []
        for idx, interval in enumerate(intervals):
            if idx == 0:
                break_point = interval[1]
                value = break_point_values.get(break_point)
                if value > 0:
                    result.append((interval, "positive"))
                elif value < 0:
                    result.append((interval, "negative"))
                elif value == 0 and slopes[0][1] > 0:
                    result.append((interval, "negative"))
                elif value == 0 and slopes[0][1] < 0:
                    result.append((interval, "positive"))
                else:
                    result.append((interval, "zero"))
            elif idx == len(intervals) - 1:
                break_point = interval[0]
                value = break_point_values.get(break_point)
                if value > 0:
                    result.append((interval, "positive"))
                elif value < 0:
                    result.append((interval, "negative"))
                elif value == 0 and slopes[-1][1] > 0:
                    result.append((interval, "positive"))
                elif value == 0 and slopes[-1][1] < 0:
                    result.append((interval, "negative"))
                else:
                    result.append((interval, "zero"))
            else:
                left = interval[0]
                left_value = break_point_values.get(left)
                right = interval[1]
                right_value = break_point_values.get(right)

                if left_value == 0 and right_value > 0:
                    result.append((interval, "positive"))
                elif right_value == 0 and left_value > 0:
                    result.append((interval, "positive"))
                else:
                    result.append((interval, "negative"))

        return result

    def __add_break_points(self, break_evens, x_1, y_1, x_2, y_2, range_slope):
        points = []
        for break_even in break_evens:
            if x_1 < break_even < x_2:
                break_x_2 = x_1 - (y_1 / range_slope)
                points.append(
                    {
                        "x_1": x_1,
                        "x_2": break_x_2,
                        "y_1": y_1,
                        "y_2": 0,
                        "slope": range_slope,
                    }
                )
                if x_2 == np.inf:
                    points.append(
                        {
                            "x_1": break_x_2,
                            "x_2": break_x_2 * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                            "y_1": 0,
                            "y_2": self.__get_right_range_y(
                                x_1=x_1,
                                y_1=y_1,
                                x_2=break_x_2 * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                                m=range_slope,
                            ),
                            "slope": range_slope,
                        }
                    )
                else:
                    points.append(
                        {
                            "x_1": break_x_2,
                            "x_2": x_2,
                            "y_1": 0,
                            "y_2": y_2,
                            "slope": range_slope,
                        }
                    )

        return points

    def get_coordinate(self):
        break_points = sorted(
            list(set(self.get_break_even().values()) | set(self.__get_unique_strikes()))
        )

        strike_values = self.__get_strike_value()
        for break_point in break_points:
            if break_point not in strike_values:
                strike_values[break_point] = 0

        slopes = self.get_slope()

        break_evens = list((self.get_break_even()).values())

        result = []
        for idx, slope in enumerate(slopes):
            range_slope = float(slope[1])
            if idx == 0:
                x_1 = 0
                x_2 = float(slope[0][1])

                y_2 = float(strike_values.get(x_2))
                y_1 = self.__get_left_range_y(x_1=x_1, x_2=x_2, y_2=y_2, m=slope[1])
            elif idx == len(slopes) - 1:
                x_1 = float(slope[0][0])
                x_2 = np.inf
                y_1 = float(strike_values.get(x_1))
                if range_slope < 0:
                    y_2 = -1 * np.inf
                elif range_slope > 0:
                    y_2 = np.inf
                else:
                    y_2 = y_1

            else:
                x_1 = float(slope[0][0])
                x_2 = float(slope[0][1])

                y_1 = float(strike_values.get(slope[0][0]))
                y_2 = float(strike_values.get(slope[0][1]))

            points = self.__add_break_points(
                break_evens=break_evens,
                x_1=x_1,
                y_1=y_1,
                x_2=x_2,
                y_2=y_2,
                range_slope=range_slope,
            )

            if points:
                result = result + points
            elif x_2 == np.inf:
                result.append(
                    {
                        "x_1": x_1,
                        "y_1": float(strike_values.get(x_1)),
                        "x_2": x_1 * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                        "y_2": self.__get_right_range_y(
                            x_1=x_1,
                            y_1=y_1,
                            x_2=x_1 * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                            m=range_slope,
                        ),
                        "slope": range_slope,
                    }
                )
            else:
                result.append(
                    {
                        "x_1": x_1,
                        "x_2": x_2,
                        "y_1": y_1,
                        "y_2": y_2,
                        "slope": range_slope,
                    }
                )

        return result


class CoveredCall:
    def __init__(self, strike, premium, asset_price) -> None:
        self.strike = strike
        self.premium = premium
        self.asset_price = asset_price
        self.name = "covered_call"
        STRATEGY_NAME_LIST.append(self.name)
        self.interval = [(-np.inf, strike), (strike, np.inf)]

    def get_slop(self):
        return {str((-np.inf, self.strike)): 1, str((self.strike, np.inf)): 0}

    def is_profit_unlimited(self):
        return False

    def is_loss_unlimited(self):
        return True

    def is_limited(self):
        return False

    def get_break_even(self):
        return self.asset_price - self.premium

    def get_break_even_points(self):
        return [
            {
                "x": self.asset_price - self.premium,
                "y": 0,
            }
        ]

    def get_profit_loss_ranges(self):
        return [
            ((-np.inf, self.get_break_even()), "negative"),
            ((self.get_break_even(), np.inf), "positive"),
        ]

    def __get_zero_price_y(self, x_1, x_2, y_2, m):
        y_1 = y_2 - (m * (x_2 - x_1))

        return float(y_1)

    def get_coordinate(self):
        results = []
        if 0 < self.get_break_even() < self.strike:
            results.append(
                {
                    "x_1": 0,
                    "y_1": self.__get_zero_price_y(
                        x_1=0,
                        x_2=self.get_break_even(),
                        y_2=0,
                        m=1,
                    ),
                    "x_2": self.get_break_even(),
                    "y_2": 0,
                    "slope": 1,
                }
            )
            results.append(
                {
                    "x_1": self.get_break_even(),
                    "y_1": 0,
                    "x_2": self.strike,
                    "y_2": self.strike + self.premium - self.asset_price,
                    "slope": 1,
                },
            )
        else:
            results = [
                {
                    "x_1": 0,
                    "y_1": self.__get_zero_price_y(
                        x_1=0,
                        x_2=self.strike,
                        y_2=self.strike + self.premium - self.asset_price,
                        m=1,
                    ),
                    "x_2": self.strike,
                    "y_2": self.strike + self.premium - self.asset_price,
                    "slope": 1,
                },
            ]

        results.append(
            {
                "x_1": self.strike,
                "y_1": self.strike + self.premium - self.asset_price,
                "x_2": self.strike * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                "y_2": self.strike + self.premium - self.asset_price,
                "slope": 0,
            }
        )

        return results


class Conversion:
    def __init__(self, strike, call_premium, put_premium, asset_price) -> None:
        self.strike = strike
        self.call_premium = call_premium
        self.put_premium = put_premium
        self.asset_price = asset_price
        self.name = "conversion"
        STRATEGY_NAME_LIST.append(self.name)
        self.interval = [(-np.inf, strike), (strike, np.inf)]
        self.net_profit = self.get_net_profit()

    def get_net_profit(self):
        return self.call_premium - self.put_premium - self.asset_price + self.strike

    def get_slop(self):
        return {str((-np.inf, self.strike)): 0, str((self.strike, np.inf)): 0}

    def is_profit_unlimited(self):
        return False

    def is_loss_unlimited(self):
        return True

    def is_limited(self):
        return False

    def get_profit_loss_ranges(self):
        if self.net_profit < 0:
            profit_sign = "negative"
        else:
            profit_sign = "positive"

        return [
            ((-np.inf, self.strike), profit_sign),
            ((self.strike, np.inf), profit_sign),
        ]

    def get_coordinate(self):
        results = []
        results.append(
            {
                "x_1": 0,
                "y_1": self.net_profit,
                "x_2": self.strike,
                "y_2": self.net_profit,
                "slope": 0,
            }
        )

        results.append(
            {
                "x_1": self.strike,
                "y_1": self.net_profit,
                "x_2": self.strike * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                "y_2": self.net_profit,
                "slope": 0,
            }
        )

        return results


class MarriedPut:
    def __init__(self, strike, put_premium, asset_price) -> None:
        self.strike = strike
        self.put_premium = put_premium
        self.asset_price = asset_price
        self.name = "married_put"
        STRATEGY_NAME_LIST.append(self.name)
        self.interval = [(-np.inf, strike), (strike, np.inf)]

    def get_slop(self):
        return {str((-np.inf, self.strike)): 0, str((self.strike, np.inf)): 1}

    def is_profit_unlimited(self):
        return True

    def is_loss_unlimited(self):
        return False

    def is_limited(self):
        return False

    def get_net_profit(self):
        return self.strike - self.put_premium - self.asset_price

    def get_break_even(self):
        return self.asset_price + self.put_premium

    def get_break_even_points(self):
        return [
            {
                "x": self.asset_price + self.put_premium,
                "y": 0,
            }
        ]

    def get_profit_loss_ranges(self):
        return [
            ((-np.inf, self.get_break_even()), "negative"),
            ((self.get_break_even(), np.inf), "positive"),
        ]

    def __get_limit_y_2(self, x_1, x_2, y_1, m):
        y_2 = y_1 + (m * (x_2 - x_1))

        return float(y_2)

    def get_coordinate(self):
        results = []
        results.append(
            {
                "x_1": 0,
                "y_1": self.get_net_profit(),
                "x_2": self.strike,
                "y_2": self.get_net_profit(),
                "slope": 0,
            }
        )
        results.append(
            {
                "x_1": self.strike,
                "y_1": self.get_net_profit(),
                "x_2": self.get_break_even(),
                "y_2": 0,
                "slope": 1,
            },
        )

        results.append(
            {
                "x_1": self.get_break_even(),
                "y_1": 0,
                "x_2": self.get_break_even() * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                "y_2": self.__get_limit_y_2(
                    x_1=self.get_break_even(),
                    y_1=0,
                    x_2=self.get_break_even() * EXTEND_POSITIVE_RANGE_COEFFICIENT,
                    m=1,
                ),
                "slope": 1,
            },
        )

        return results
