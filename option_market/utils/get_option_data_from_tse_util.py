import jdatetime
import pandas as pd
from core.utils import replace_arabic_letters_pd
from stock_market.utils import get_last_market_watch_data

ENGLISH_COLUMNS = {
    "lva": "symbol",
    "lvc": "name",
    "ztt": "number",
    "qtc": "value",
    "qtj": "volume",
    "py": "yesterday",
    "pf": "first",
    "pc": "last_changes",
    "pcl": "close",
    "pcpc": "close_changes",
    "pmn": "min",
    "pmx": "max",
    "pMax": "max_price",
    "pMin": "min_price",
    "pClosing": "close_price",
    "qmd": "best_buy_volume",
    "zmd": "best_buy_number",
    "pmd": "best_buy_price",
    "pmo": "best_sell_price",
    "zmo": "best_sell_number",
    "qmo": "best_sell_volume",
    "insCode": "inst_id",
    "hEven": "last_update",
}

UNNECESSARY_COLUMNS = [
    "vc",
    "csv",
    "ztd",
    "id",
    "iClose",
    "yClose",
    "qTotTran5J",
    "bv",
    "pdv",
    "zTotTran",
    "qTotCap",
    "pDrCotVal",
    "eps",
    "pe",
    "insID",
    "dEven",
    "blDs",
]


def extract_buy_and_sell_info_from_bIDs(row) -> tuple:
    info = row["blDs"][0]
    qmd = info["qmd"]
    zmd = info["zmd"]
    pmd = info["pmd"]
    pmo = info["pmo"]
    zmo = info["zmo"]
    qmo = info["qmo"]

    return qmd, zmd, pmd, pmo, zmo, qmo


def edit_last_update(row):
    last_update = str(row.get("last_update"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def get_option_data_from_tse() -> pd.DataFrame:

    last_options = get_last_market_watch_data()
    if last_options.empty:
        return pd.DataFrame()

    last_options["lvc"] = last_options.apply(
        replace_arabic_letters_pd, axis=1, args=("lvc",)
    )
    last_options["lva"] = last_options.apply(
        replace_arabic_letters_pd, axis=1, args=("lva",)
    )

    last_options = last_options[last_options["lvc"].str.contains("اختیار")]
    if last_options.empty:
        return pd.DataFrame()

    last_options[["qmd", "zmd", "pmd", "pmo", "zmo", "qmo"]] = last_options.apply(
        extract_buy_and_sell_info_from_bIDs,
        axis=1,
        result_type="expand",
    )

    last_options.drop(columns=UNNECESSARY_COLUMNS, inplace=True)
    last_options.rename(columns=ENGLISH_COLUMNS, inplace=True)
    last_options = last_options[last_options["last_update"] > 80000]
    last_options["last_update"] = last_options.apply(edit_last_update, axis=1)

    return last_options
