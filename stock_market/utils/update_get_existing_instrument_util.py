from core.utils import get_http_response, replace_all_arabic_letters_in_db
from stock_market.models import StockInstrument, StockIndustrialGroup
from .used_dicts_util import (
    TSETMC_REQUEST_HEADERS,
    ALL_PAPER_TYPE_DICT,
    MAIN_MARKET_TYPE_DICT,
)


def update_get_existing_instrument():
    for market_type_num in MAIN_MARKET_TYPE_DICT.keys():
        for paper_type_num in ALL_PAPER_TYPE_DICT.keys():
            URL = (
                f"https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"
                f"?market={market_type_num}"
                f"&paperTypes[0]={paper_type_num}"
                "&showTraded=false"
            )

            response = get_http_response(
                req_url=URL, req_headers=TSETMC_REQUEST_HEADERS
            )
            response = response.json()
            response = response.get("marketwatch")

            for instrument in response:
                ins_code = instrument.get("insCode")
                try:
                    StockInstrument.objects.get(ins_code=ins_code)
                except StockInstrument.DoesNotExist:
                    new_instrument = dict()
                    new_instrument["ins_code"] = ins_code
                    industrial_group_code = int((instrument.get("csv")).strip())
                    new_instrument["industrial_group"] = (
                        StockIndustrialGroup.objects.get(code=industrial_group_code)
                    )
                    new_instrument["market_type"] = market_type_num
                    new_instrument["paper_type"] = paper_type_num
                    new_instrument["ins_id"] = instrument.get("insID")
                    new_instrument["symbol"] = instrument.get("lva")
                    new_instrument["name"] = instrument.get("lvc")

                    new_instrument = StockInstrument(**new_instrument)
                    new_instrument.save()

    replace_all_arabic_letters_in_db()
