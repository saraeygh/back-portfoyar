MAIN_MARKET_TYPE_DICT = {
    1: "بورس",
    2: "فرابورس",
}

ALL_MARKET_TYPE_DICT = {0: "بورس و فرابورس", **MAIN_MARKET_TYPE_DICT}

STOCK_PAPER = 1
INITIAL_MARKET_PAPER = 2
ACCOMMODATION_PAPER = 3
PRIORITY_PAPER = 4
DEBT_PAPER = 5
OPTION_PAPER = 6
FUTURE_PAPER = 7
FUND_PAPER = 8
COMMODITY_PAPER = 9

MAIN_PAPER_TYPE_DICT = {
    STOCK_PAPER: "سهام",
    INITIAL_MARKET_PAPER: "بازار پایه فرابورس",
    FUND_PAPER: "صندوق‌های سرمایه‌گذاری",
    PRIORITY_PAPER: "حق تقدم",
}

ALL_PAPER_TYPE_DICT = {
    **MAIN_PAPER_TYPE_DICT,
    ACCOMMODATION_PAPER: "تسهیلات مسکن",
    DEBT_PAPER: "اوراق بدهی",
    OPTION_PAPER: "اختیار معامله",
    FUTURE_PAPER: "آتی",
    COMMODITY_PAPER: "بورس کالا",
}


MARKET_WATCH_COLUMN_RENAME = {
    "lva": "symbol",
    "lvc": "name",
    "pmd": "buy_price",
    "pmo": "sell_price",
    "qtj": "volume",
    "pdv": "last_price",
    "ztt": "trade_count",
    "qtc": "value",
    "bv": "base_volume",
    "pc": "last_price_change",
    "pcpc": "closing_price_change",
    "pmn": "min_price",
    "pmx": "max_price",
    "py": "yesterday_price",
    "pf": "first_price",
    "pcl": "closing_price",
    "vc": "vc",
    "csv": "csv",
    "insID": "ins_id",
    "pMax": "valid_max_price",
    "pMin": "valid_min_price",
    "ztd": "share_count",
    "blDs": "order_book",
    "insCode": "ins_code",
    "dEven": "dEven",
    "hEven": "last_time",
    "pClosing": "pClosing",
    "iClose": "iClose",
    "yClose": "yClose",
    "pDrCotVal": "pDrCotVal",
    "zTotTran": "zTotTran",
    "qTotTran5J": "qTotTran5J",
    "zTotCap": "zTotCap",
    "buy_CountI": "person_buy_count",
    "buy_I_Volume": "person_buy_volume",
    "sell_CountI": "person_sell_count",
    "sell_I_Volume": "person_sell_volume",
    "buy_CountN": "legal_buy_count",
    "buy_N_Volume": "legal_buy_volume",
    "sell_CountN": "legal_sell_count",
    "sell_N_Volume": "legal_sell_volume",
    "buy_DDD_Volume": "buy_DDD_Volume",
    "sell_DDD_Volume": "sell_DDD_Volume",
    "buy_CountDDD": "buy_CountDDD",
    "sell_CountDDD": "sell_CountDDD",
}

HISTORY_COLUMN_RENAME = {
    "date": "trade_date",
    "zTotTran": "trade_count",
    "qTotCap": "value",
    "qTotTran5J": "volume",
    "pClosing": "close_mean",
    "priceYesterday": "yesterday_price",
    "priceMin": "low",
    "priceMax": "high",
    "priceFirst": "open",
    "pDrCotVal": "close",
    "buy_I_Count": "individual_buy_count",
    "buy_I_Volume": "individual_buy_volume",
    "buy_I_Value": "individual_buy_value",
    "buy_N_Count": "legal_buy_count",
    "buy_N_Volume": "legal_buy_volume",
    "buy_N_Value": "legal_buy_value",
    "sell_I_Count": "individual_sell_count",
    "sell_I_Volume": "individual_sell_volume",
    "sell_I_Value": "individual_sell_value",
    "sell_N_Count": "legal_sell_count",
    "sell_N_Volume": "legal_sell_volume",
    "sell_N_Value": "legal_sell_value",
}

INDIVIDUAL_LEGAL_HISTORY_COLUMN_RENAME = {
    "buy_I_Count": "individual_buy_count",
    "buy_I_Volume": "individual_buy_volume",
    "buy_I_Value": "individual_buy_value",
    "buy_N_Count": "legal_buy_count",
    "buy_N_Volume": "legal_buy_volume",
    "buy_N_Value": "legal_buy_value",
    "sell_I_Count": "individual_sell_count",
    "sell_I_Volume": "individual_sell_volume",
    "sell_I_Value": "individual_sell_value",
    "sell_N_Count": "legal_sell_count",
    "sell_N_Volume": "legal_sell_volume",
    "sell_N_Value": "legal_sell_value",
    "date": "trade_date",
}


VOLUME_CHANGE_COLS = {
    "insCode": "ins_code",
    "lva": "symbol",
    "lvc": "name",
    "hEven": "last_update",
    "qtc": "value",
    "ztt": "trade_count",
    "qtj": "volume",
    "py": "yesterday_price",
    "pcl": "closing_price",
    "pdv": "last_price",
    "pc": "last_price_change",
    "pcpc": "closing_price_change",
}


MARKET_WATCH_COLS = {
    "lva": "symbol",
    "lvc": "name",
    "pmd": "buy_price",
    "pmo": "sell_price",
    "qtj": "volume",
    "pdv": "last_price",
    "ztt": "trade_count",
    "qtc": "value",
    "bv": "base_volume",
    "pc": "last_price_change",
    "pcpc": "closing_price_change",
    "pmn": "min_price",
    "pmx": "max_price",
    "py": "yesterday_price",
    "pf": "first_price",
    "pcl": "closing_price",
    "vc": "vc",
    "csv": "csv",
    "insID": "ins_id",
    "pMax": "valid_max_price",
    "pMin": "valid_min_price",
    "ztd": "share_count",
    "blDs": "order_book",
    "insCode": "ins_code",
    "dEven": "last_date",
    "hEven": "last_time",
}


INDIVIDUAL_LEGAL_COLS = {
    "insCode": "ins_code",
    "buy_CountI": "individual_buy_count",
    "buy_I_Volume": "individual_buy_volume",
    "buy_CountN": "legal_buy_count",
    "buy_N_Volume": "legal_buy_volume",
    "sell_CountI": "individual_sell_count",
    "sell_I_Volume": "individual_sell_volume",
    "sell_CountN": "legal_sell_count",
    "sell_N_Volume": "legal_sell_volume",
}
