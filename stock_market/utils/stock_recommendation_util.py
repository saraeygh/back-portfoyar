import pandas as pd

from core.utils import MongodbInterface
from core.configs import (
    STOCK_MONGO_DB,
    STOCK_NA_ROI,
    GLOBAL_MONGO_DB,
    DOMESTIC_MONGO_DB,
)
from global_market.models import GlobalRelation
from domestic_market.models import DomesticRelation
from stock_market.models import RecommendationConfig


def result_from_mongo(db, collection):
    result = MongodbInterface(db_name=db, collection_name=collection)
    result = result.collection.find({}, {"_id": 0})
    result = pd.DataFrame(result)

    return result


def calculate_score(
    df, idx_column, score_column, min_value, max_value, score_min, score_max
):
    df[score_column] = (
        ((df[idx_column] - min_value) / (max_value - min_value))
        * (score_max - score_min)
    ) + score_min

    return df


def get_score(df, idx_column, score_column, config, min_value, max_value):
    if max_value <= 0:
        if config.ascending:
            score_min = 0
            score_max = config.weight
        else:
            score_min = -1 * config.weight
            score_max = 0

        df = calculate_score(
            df=df,
            idx_column=idx_column,
            score_column=score_column,
            min_value=min_value,
            max_value=max_value,
            score_min=score_min,
            score_max=score_max,
        )

    elif max_value > 0 and min_value < 0:
        if config.ascending:
            score_min = -1 * config.weight
            score_max = config.weight
        else:
            score_min = config.weight
            score_max = -1 * config.weight

        df_positive = df[df[idx_column] >= 0]
        df_positive = calculate_score(
            df=df_positive,
            idx_column=idx_column,
            score_column=score_column,
            min_value=df_positive[idx_column].min(),
            max_value=df_positive[idx_column].max(),
            score_min=0,
            score_max=score_max,
        )

        df_negative = df[df[idx_column] < 0]
        df_negative = calculate_score(
            df=df_negative,
            idx_column=idx_column,
            score_column=score_column,
            min_value=df_negative[idx_column].min(),
            max_value=df_negative[idx_column].max(),
            score_min=score_min,
            score_max=0,
        )

        df = pd.concat([df_positive, df_negative])

    else:
        if config.ascending:
            score_min = 0
            score_max = config.weight
        else:
            score_min = 0
            score_max = -1 * config.weight

        df = calculate_score(
            df=df,
            idx_column=idx_column,
            score_column=score_column,
            min_value=min_value,
            max_value=max_value,
            score_min=score_min,
            score_max=score_max,
        )

    return df


def get_market_watch_result(conf):
    idx_dict = {
        "money_flow": conf.money_flow,
        "buy_pressure": conf.buy_pressure,
        "buy_value": conf.buy_value,
        "buy_ratio": conf.buy_ratio,
        "sell_ratio": conf.sell_ratio,
    }

    result_dict = {}
    for name, config in idx_dict.items():
        score_column = f"{name}_score"
        if config.is_enabled:
            try:
                result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
                result = result[["ins_code", name]]
                result = result[result[name] >= config.threshold_value]
            except Exception:
                continue

            min_value = result[name].min()
            max_value = result[name].max()
            result = get_score(
                df=result,
                idx_column=name,
                score_column=score_column,
                config=config,
                min_value=min_value,
                max_value=max_value,
            )
            result = result.groupby("ins_code").mean().reset_index()

            result_dict[name] = result

        else:
            continue

    return result_dict


def get_roi_result(config):
    durations = {
        7: "weekly",
        30: "monthly",
        90: "quarterly",
        180: "half_yearly",
        365: "yearly",
        1095: "three_years",
    }

    name = "roi"
    idx_name = f"{durations.get(config.duration)}_{name}"
    score_column = f"{name}_score"
    if config.is_enabled:
        try:
            result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
            result = result[["ins_code", idx_name]]
            result = result[result[idx_name] != STOCK_NA_ROI]
            result = result[result[idx_name] >= config.threshold_value]
        except Exception:
            return pd.DataFrame()

        min_value = result[idx_name].min()
        max_value = result[idx_name].max()
        result = get_score(
            df=result,
            idx_column=idx_name,
            score_column=score_column,
            config=config,
            min_value=min_value,
            max_value=max_value,
        )
        result = result.groupby("ins_code").mean().reset_index()
        result = result.rename(columns={idx_name: "roi"})

        return result

    else:
        return pd.DataFrame()


def get_value_change_result(config):

    name = "value_change"
    score_column = f"{name}_score"
    if config.is_enabled:
        result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
        try:
            result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
            result = result[["ins_code", name]]
            result = result[result[name] >= config.threshold_value]
        except Exception:
            return pd.DataFrame()

        min_value = result[name].min()
        max_value = result[name].max()
        result = get_score(
            df=result,
            idx_column=name,
            score_column=score_column,
            config=config,
            min_value=min_value,
            max_value=max_value,
        )
        result = result.groupby("ins_code").mean().reset_index()

        return result

    else:
        return pd.DataFrame()


def get_option_value_change_result(conf):
    idx_dict = {
        "call_value_change": conf.call_value_change,
        "put_value_change": conf.put_value_change,
    }

    result_dict = {}
    idx_name = "value_change"
    for name, config in idx_dict.items():
        score_column = f"{name}_score"
        if config.is_enabled:
            try:
                result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
                result = result[["ins_code", idx_name]]
                result = result[result[idx_name] >= config.threshold_value]
            except Exception:
                continue

            min_value = result[idx_name].min()
            max_value = result[idx_name].max()
            result = get_score(
                df=result,
                idx_column=idx_name,
                score_column=score_column,
                config=config,
                min_value=min_value,
                max_value=max_value,
            )

            result = result.rename(columns={idx_name: name})
            result = result.groupby("ins_code").mean().reset_index()

            result_dict[name] = result

        else:
            continue

    return result_dict


def get_option_price_spread_result(config):

    name = "option_price_spread"
    idx_name = "monthly_price_spread"
    score_column = f"{name}_score"
    if config.is_enabled:
        try:
            result = result_from_mongo(db=STOCK_MONGO_DB, collection=name)
            result = result[["ins_code", idx_name]]
            result = result[result[idx_name] >= config.threshold_value]
        except Exception:
            return pd.DataFrame()

        min_value = result[idx_name].min()
        max_value = result[idx_name].max()
        result = get_score(
            df=result,
            idx_column=idx_name,
            score_column=score_column,
            config=config,
            min_value=min_value,
            max_value=max_value,
        )

        result = result.rename(columns={idx_name: name})
        result = result.groupby("ins_code").mean().reset_index()

        return result

    else:
        return pd.DataFrame()


def get_global_result(conf):
    idx_dict = {
        "global_positive_range": conf.global_positive_range,
        "global_negative_range": conf.global_negative_range,
    }

    result_dict = {}
    idx_name = "deviation"
    for name, config in idx_dict.items():
        score_column = f"{name}_score"
        if config.is_enabled:
            collection_name_dict = {
                7: "one_week_mean",
                30: "one_month_mean",
                90: "three_month_mean",
                180: "six_month_mean",
                365: "one_year_mean",
            }
            collection = collection_name_dict.get(config.duration)

            try:
                result = result_from_mongo(db=GLOBAL_MONGO_DB, collection=collection)
                if name == "global_positive_range":
                    result = result[result[idx_name] > config.threshold_value]
                else:
                    result = result[result[idx_name] < config.threshold_value]

                result = result[["commodity_type", idx_name]]
                result = result.groupby("commodity_type").mean().reset_index()
            except Exception:
                continue

            min_value = result[idx_name].min()
            max_value = result[idx_name].max()
            result = get_score(
                df=result,
                idx_column=idx_name,
                score_column=score_column,
                config=config,
                min_value=min_value,
                max_value=max_value,
            )

            related_stock = pd.DataFrame()
            for _, row in result.iterrows():
                relations = GlobalRelation.objects.filter(
                    global_commodity_type__name=str(row["commodity_type"])
                )
                if relations.exists():
                    relations = relations.values(
                        "stock_instrument__ins_code", "stock_instrument__symbol"
                    )
                    relations = pd.DataFrame(relations)
                    relations["deviation"] = float(row["deviation"])
                    relations[score_column] = float(row[score_column])
                    related_stock = pd.concat([related_stock, relations])
                else:
                    continue

            try:
                related_stock = related_stock.rename(
                    columns={"stock_instrument__ins_code": "ins_code"}
                )
                related_stock = related_stock[["ins_code", idx_name, score_column]]
                related_stock = related_stock.rename(columns={idx_name: name})
                related_stock = related_stock.groupby("ins_code").mean().reset_index()
                result_dict[name] = related_stock
            except Exception:
                continue

        else:
            continue

    return result_dict


def get_domestic_result(conf):
    idx_dict = {
        "domestic_positive_range": conf.domestic_positive_range,
        "domestic_negative_range": conf.domestic_negative_range,
    }

    result_dict = {}
    idx_name = "deviation"
    for name, config in idx_dict.items():
        score_column = f"{name}_score"
        if config.is_enabled:
            collection_name_dict = {
                7: "one_week_mean",
                30: "one_month_mean",
                90: "three_month_mean",
                180: "six_month_mean",
                365: "one_year_mean",
            }
            collection = collection_name_dict.get(config.duration)

            try:
                result = result_from_mongo(db=DOMESTIC_MONGO_DB, collection=collection)
                if name == "domestic_positive_range":
                    result = result[result[idx_name] > config.threshold_value]
                else:
                    result = result[result[idx_name] < config.threshold_value]

                result = result[["producer_code", idx_name]]
                result = result.groupby("producer_code").mean().reset_index()
            except Exception:
                continue

            min_value = result[idx_name].min()
            max_value = result[idx_name].max()
            result = get_score(
                df=result,
                idx_column=idx_name,
                score_column=score_column,
                config=config,
                min_value=min_value,
                max_value=max_value,
            )

            related_stock = pd.DataFrame()
            for _, row in result.iterrows():
                relations = DomesticRelation.objects.filter(
                    domestic_producer__code=int(row["producer_code"])
                )
                if relations.exists():
                    relations = relations.values(
                        "stock_instrument__ins_code", "stock_instrument__symbol"
                    )
                    relations = pd.DataFrame(relations)
                    relations["deviation"] = float(row["deviation"])
                    relations[score_column] = float(row[score_column])
                    related_stock = pd.concat([related_stock, relations])
                else:
                    continue

            try:
                related_stock = related_stock.rename(
                    columns={"stock_instrument__ins_code": "ins_code"}
                )
                related_stock = related_stock[["ins_code", idx_name, score_column]]
                related_stock = related_stock.rename(columns={idx_name: name})
                related_stock = related_stock.groupby("ins_code").mean().reset_index()
                result_dict[name] = related_stock
            except Exception:
                continue

        else:
            continue

    return result_dict


def add_link(row) -> str:
    ins_code = str(row["ins_code"])
    inst_link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return inst_link


def stock_recommendation(config: RecommendationConfig):

    results = get_market_watch_result(config)
    results["roi"] = get_roi_result(config.roi)
    results["value_change"] = get_value_change_result(config.value_change)
    results.update(get_option_value_change_result(config))
    results["option_price_spread"] = get_option_price_spread_result(
        config.option_price_spread
    )
    results.update(get_global_result(config))
    results.update(get_domestic_result(config))

    scores = pd.concat(list(results.values()))
    if scores.empty:
        return scores
    scores = scores.fillna(0)
    scores = scores.groupby("ins_code").sum().reset_index()

    instruments = result_from_mongo(db=STOCK_MONGO_DB, collection="instrument_info")
    instruments = pd.DataFrame(instruments)
    instruments = instruments[["ins_code", "symbol"]]

    scores = pd.merge(left=scores, right=instruments, on="ins_code", how="left")
    scores = scores[~scores["symbol"].astype(str).str.contains(r"\d")]

    score_columns = [col for col in scores.columns if col.endswith("score")]
    scores["total_score"] = scores[score_columns].sum(axis=1)

    scores["link"] = scores.apply(add_link, axis=1)

    return scores
