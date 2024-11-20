from io import BytesIO
import os
import re

import numpy as np
import pandas as pd
from core.utils import send_upload_error_file_email, clear_redis_cache
from django.core.files.storage import default_storage
from global_market.serializers import GlobalTradeSerializer
from global_market.utils import populate_global_market_db
from global_market.tasks import calculate_commodity_means_global
from samaneh.settings.common import BASE_DIR
from tqdm import tqdm
from colorama import Fore, Style

EXTRACT_PATTERN_UNIT = r"\((.*?)\)"
EXTRACT_PATTERN_TRANSIT_1 = r"\((.*?\))\)"
EXTRACT_PATTERN_TRANSIT_2 = r"\((.*?\(.*?\).*?)\)"
EXTRACT_PATTERN_TRANSIT_3 = r"\((.*?)\)"


def get_sheet_names(excel_file):
    xls = pd.ExcelFile(BytesIO(excel_file))
    sheet_names_list = xls.sheet_names

    return sheet_names_list


def add_unit_column(row):
    raw_market = row["market"]
    matches = re.findall(EXTRACT_PATTERN_UNIT, raw_market)
    if matches:
        unit = matches[-1]
    else:
        unit = None

    return unit


def remove_unit_from_market(row):
    raw_market = row["market"]
    raw_unit = row["unit"]

    market = raw_market.replace(f"({raw_unit})", "")

    return market


def add_transit_column(row):
    raw_market = row["market"]
    matches_transit_1 = re.findall(EXTRACT_PATTERN_TRANSIT_1, raw_market)
    matches_transit_2 = re.findall(EXTRACT_PATTERN_TRANSIT_2, raw_market)
    matches = re.findall(EXTRACT_PATTERN_TRANSIT_3, raw_market)
    if matches_transit_1:
        transit = matches_transit_1[-1]
    elif matches_transit_2:
        transit = matches_transit_2[-1]
    elif matches:
        transit = matches[-1]
    else:
        transit = None

    return transit


def remove_transit_from_market(row):
    raw_market = row["market"]
    raw_transit = row["transit"]

    market = raw_market.replace(f"({raw_transit})", "")

    return market


def add_industry(row, sheet_name):
    INDUSTRIES = {
        "aps": "محصولات شیمیایی",
        "apag": "محصولات پالایشی",
        "lpg": "ال پی جی",
        "argus_nit": "محصولات شیمیایی",
        "argus_base_oil": "محصولات پالایشی",
        "steel": "فلزات",
        "steel_raw": "مواد معدنی",
    }

    industry = INDUSTRIES.get(sheet_name)
    industry = industry if industry else None

    return industry


def add_commodity_type(row):
    COMMODITY_TYPES = {
        "abs inj": "abs inj",
        "block copol": "block copol",
        "bopp": "bopp",
        "benzene": "بنزن",
        "butadiene": "بوتادین",
        "ethylene": "اتیلن",
        "hdpe": "پلی اتیلن سنگین",
        "hips": "hips",
        "ipp film": "ipp film",
        "iso-mx": "iso-mx",
        "ldpe": "پلی اتیلن سبک",
        "meg": "meg",
        "mma": "mma",
        "methanol": "متانول",
        "ox": "ox",
        "pet": "پت",
        "pmma": "pmma",
        "pp injection": "pp injection",
        "pp raffia": "pp raffia",
        "ps gœp": "ps gœp",
        "pta": "pta",
        "pvc": "پی وی سی",
        "px": "px",
        "polyester": "پلی استر",
        "propylene": "پروپیلن",
        "sol-mx": "sol-mx",
        "styrene": "استایرن",
        "toluene": "تولئن",
        "bitumen": "قیر",
        "condensate": "میعانات گازی",
        "cst": "cst",
        "gasoil": "گازوئیل",
        "gasoline ": "بنزین",
        "hsfo": "نفت کوره",
        "jet": "نفت سفید",
        "kerosene": "نفت سفید",
        "mtbe": "متیل ترشیو بوتیل",
        "marine fuel": "نفت کوره",
        "naphtha": "نفتا",
        "butane": "بوتان",
        "lpg": "ال پی جی",
        "propane": "پروپان",
        "ammonium nitrate": "آمونیوم نیترات",
        "urea": "اوره",
        "sn 500": "روغن پایه",
        "sn 150": "روغن پایه",
        "n70": "روغن پایه",
        "n500": "روغن پایه",
        "n150": "روغن پایه",
        "bright stock": "روغن پایه",
        "8cst": "روغن پایه",
        "6cst": "روغن پایه",
        "4cst": "روغن پایه",
        "steel billet": "بیلت فولادی",
        "steel cold": "ورق سرد",
        "galvanized": "گالوانیزه",
        "steel hot": "ورق گرم",
        "steel reinforcing": "فولاد آلیاژی",
        "steel slab": "اسلب فولادی",
        "coke": "ذغال سنگ",
        "direct reduced iron": "آهن اسفنجی",
        "pig iron": "آهن قراضه",
        "coking": "ذغال سنگ",
        "iron ore": "سنگ آهن",
    }

    commodity = row["commodity"]

    for key in COMMODITY_TYPES.keys():
        if key in commodity.lower():
            commodity_type = COMMODITY_TYPES.get(key)
            return commodity_type
        else:
            commodity_type = None

    return commodity_type


def convert_trades_columns_to_one(row):
    VALID_DATE_PATTERN = r"[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))"
    row_dict = row.to_dict()

    trades = {}
    for key, value in row_dict.items():
        match = re.match(VALID_DATE_PATTERN, key)
        if match:
            trades[key] = value

    return trades


def upload_xlsx_data_task(excel_file_name: str) -> None:
    with default_storage.open(
        f"{BASE_DIR}/media/uploaded_files/{excel_file_name}"
    ) as file:
        excel_file = file.read()

    excel_sheet_names_list = get_sheet_names(excel_file)
    for sheet_name in excel_sheet_names_list:
        print(
            Fore.GREEN
            + f"************************************** Uploading {sheet_name}"
            + Style.RESET_ALL
        )

        market_df = pd.read_excel(io=BytesIO(excel_file), sheet_name=sheet_name)

        market_df["unit"] = market_df.apply(add_unit_column, axis=1)
        market_df["market"] = market_df.apply(remove_unit_from_market, axis=1)

        market_df["transit"] = market_df.apply(add_transit_column, axis=1)
        market_df["market"] = market_df.apply(
            remove_transit_from_market,
            axis=1,
        )
        market_df = market_df.rename(columns={"market": "commodity"})

        market_df["industry"] = market_df.apply(
            add_industry, axis=1, sheet_name=sheet_name
        )

        market_df["commodity_type"] = market_df.apply(
            add_commodity_type,
            axis=1,
        )

        market_df = market_df.replace(np.nan, None)

        market_df["trades"] = market_df.apply(
            convert_trades_columns_to_one,
            axis=1,
        )

        global_market_list_of_dict = market_df.to_dict(orient="records")

        valid_global_market_list_of_dict = []
        invalid_global_market_list_of_dict = []
        for global_market in tqdm(
            global_market_list_of_dict, desc=f"Serializing {sheet_name}", ncols=10
        ):
            global_market_srz = GlobalTradeSerializer(data=global_market)
            if global_market_srz.is_valid():
                valid_global_market_list_of_dict.append(
                    global_market_srz.validated_data
                )
            else:
                for field, error_list in global_market_srz.errors.items():
                    errors = []
                    for error in error_list:
                        error_str = str(error)
                        errors.append(error_str)

                    global_market["error_" + field] = errors

                invalid_global_market_list_of_dict.append(global_market)

        if invalid_global_market_list_of_dict:
            print(Fore.BLUE + "Sending invalid records email" + Style.RESET_ALL)
            unvalid_global_market_df = pd.DataFrame(invalid_global_market_list_of_dict)

            save_dir = f"{BASE_DIR}/media/uploaded_files/"
            is_dir = os.path.isdir(save_dir)
            if not is_dir:
                os.makedirs(save_dir)

            file_name = "invalid_global_market.csv"
            file_path = save_dir + file_name
            unvalid_global_market_df.to_csv(file_path, index=False)

            send_upload_error_file_email(file_path=file_path, task_name="بازار جهانی")

        if len(valid_global_market_list_of_dict) == 0:
            continue

        populate_global_market_db(valid_global_market_list_of_dict)

        print(
            Fore.GREEN + "**************************************"
            f" Uploaded {sheet_name}, {len(global_market_list_of_dict)} records."
            + Style.RESET_ALL
        )

    print(
        Fore.GREEN
        + Style.BRIGHT
        + "************************************** Uploaded data successfully."
        + Style.RESET_ALL
    )
    calculate_commodity_means_global()
    clear_redis_cache()
