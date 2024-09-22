import re

import jdatetime
import pandas as pd

# from .get_assets_data_util import get_assets_base_equit_price

CORRECT_ASSET_NAMES_DICT = {
    "حافرين": "حآفرين",
    "ص آگاه": "پتروآگاه",
    "ص.دارا": "دارا يكم",
}


def add_strike(row) -> int:
    strike = str(row.get("name"))
    strike = strike.split("-")
    strike = strike[1]
    strike = int(strike)

    return strike


def add_asset_name(row) -> str:
    asset_name = " ".join(row["name"].split("-")[0].split(" ")[1:])

    return asset_name


def add_option_type(row) -> str:
    full_name = str(row.get("name"))

    if "اختیارخ" in full_name:
        return "call"
    elif "اختیارف" in full_name:
        return "put"
    else:
        return "NA"


def add_option_expiry_date(row) -> str:
    exp_date = "1397/01/01"

    YYYY_MM_DD_pattern = r"(\d{4}\/\d{2}\/\d{2})"
    match_YYYY_MM_DD = re.search(YYYY_MM_DD_pattern, row["name"])
    if match_YYYY_MM_DD:
        exp_date = match_YYYY_MM_DD.group(0)

    YY_MM_DD_pattern = r"(\d{2}\/\d{2}\/\d{2})"
    match_YY_MM_DD = re.search(YY_MM_DD_pattern, row["name"])
    if match_YY_MM_DD:
        exp_date = "14" + match_YY_MM_DD.group(0)

    YYYYMMDD_pattern = r"[\d]{8}"
    match_YYYYMMDD = re.search(YYYYMMDD_pattern, row["name"])
    if match_YYYYMMDD:
        exp_date = match_YYYYMMDD.group(0)
        exp_date = f"{exp_date[:4]}/{exp_date[4:6]}/{exp_date[6:]}"

    YYMMDD_pattern = r"[\d]{6}$"
    match_YYMMDD = re.search(YYMMDD_pattern, row["name"])
    if match_YYMMDD:
        exp_date = "14" + match_YYMMDD.group(0)
        exp_date = f"{exp_date[:4]}/{exp_date[4:6]}/{exp_date[6:]}"

    return exp_date


def add_days_to_expire(row) -> int:
    year, month, day = map(int, row["expiration_date"].split("/"))
    expiration_date = jdatetime.date(year, month, day, locale="fa_IR")
    today_date = jdatetime.date.today()
    days_to_expire = (expiration_date - today_date).days

    return days_to_expire


def add_link(row) -> str:
    inst_id = str(row["inst_id"])
    inst_link = f"https://main.tsetmc.com/InstInfo/{inst_id}/"

    return inst_link


def add_additional_columns(options_df: pd.DataFrame) -> pd.DataFrame:
    options_df["strike"] = options_df.apply(add_strike, axis=1)

    options_df["asset_name"] = options_df.apply(add_asset_name, axis=1)
    options_df["asset_name"] = options_df["asset_name"].replace(
        CORRECT_ASSET_NAMES_DICT
    )

    options_df["option_type"] = options_df.apply(add_option_type, axis=1)
    options_df["expiration_date"] = options_df.apply(add_option_expiry_date, axis=1)
    options_df["days_to_expire"] = options_df.apply(add_days_to_expire, axis=1)
    options_df["link"] = options_df.apply(add_link, axis=1)

    assets_base_equit_price_df = get_assets_base_equit_price()
    assets_base_equit_price_df = assets_base_equit_price_df[
        ["short_name", "base_equit_price"]
    ]

    options_df = pd.merge(
        left=options_df,
        right=assets_base_equit_price_df,
        left_on="asset_name",
        right_on="short_name",
        how="left",
    )

    options_df.drop("short_name", inplace=True, axis=1)

    return options_df
