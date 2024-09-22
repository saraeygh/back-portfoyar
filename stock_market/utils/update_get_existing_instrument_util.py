from core.utils import get_http_response, replace_all_arabic_letters_in_db
from stock_market.models import StockInstrument
from .used_dicts_util import (
    TSETMC_REQUEST_HEADERS,
    ALL_PAPER_TYPE_DICT,
    MAIN_MARKET_TYPE_DICT,
)


def update_get_existing_instrument(existing_industrial_group: dict):
    instrument_list = StockInstrument.objects.all()

    existing_instrument_dict = dict()
    for instrument in instrument_list:
        existing_instrument_dict[instrument.ins_code] = instrument
    del instrument_list

    instrument_bulk_list = []
    for market_type_num in MAIN_MARKET_TYPE_DICT.keys():
        for paper_type_num in ALL_PAPER_TYPE_DICT.keys():
            URL = f"https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch?market={market_type_num}&industrialGroup="
            URL += f"&paperTypes[0]={paper_type_num}"
            URL += "&showTraded=false&withBestLimits=true"

            response = get_http_response(
                req_url=URL, req_headers=TSETMC_REQUEST_HEADERS
            )

            try:
                response = response.json()
                response = response.get("marketwatch")
            except Exception:
                response = []

            if response:
                for instrument in response:
                    ins_code = instrument.get("insCode")
                    if ins_code not in existing_instrument_dict:
                        new_instrument = dict()
                        new_instrument["ins_code"] = ins_code
                        industrial_group_code = int((instrument.get("csv")).strip())
                        new_instrument["industrial_group"] = (
                            existing_industrial_group.get(industrial_group_code)
                        )

                        new_instrument["market_type"] = market_type_num
                        new_instrument["paper_type"] = paper_type_num
                        new_instrument["ins_id"] = instrument.get("insID")
                        new_instrument["symbol"] = instrument.get("lva")
                        new_instrument["name"] = instrument.get("lvc")

                        new_instrument = StockInstrument(**new_instrument)
                        instrument_bulk_list.append(new_instrument)
                        existing_instrument_dict[ins_code] = new_instrument

    if instrument_bulk_list:
        StockInstrument.objects.bulk_create(instrument_bulk_list)

    replace_all_arabic_letters_in_db()

    return existing_instrument_dict
