from core.utils import (
    TSETMC_REQUEST_HEADERS,
    get_http_response,
    replace_all_arabic_letters_in_db,
)
from stock_market.models import StockInstrument, StockIndustrialGroup
from .used_dicts_util import ALL_PAPER_TYPE_DICT, MAIN_MARKET_TYPE_DICT


def update_get_existing_instrument():
    bulk_update_list = []
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
                industrial_group_code = int((instrument.get("csv")).strip())
                industrial_group = StockIndustrialGroup.objects.get(
                    code=industrial_group_code
                )
                ins_id = instrument.get("insID")
                symbol = instrument.get("lva")
                name = instrument.get("lvc")

                try:
                    ex_instrument = StockInstrument.objects.get(ins_code=ins_code)
                    ex_instrument.market_type = market_type_num
                    ex_instrument.paper_type = paper_type_num
                    ex_instrument.ins_id = ins_id
                    ex_instrument.symbol = symbol
                    ex_instrument.name = name
                    bulk_update_list.append(ex_instrument)
                except StockInstrument.DoesNotExist:
                    new_instrument = dict()
                    new_instrument["ins_code"] = ins_code
                    new_instrument["industrial_group"] = industrial_group
                    new_instrument["market_type"] = market_type_num
                    new_instrument["paper_type"] = paper_type_num
                    new_instrument["ins_id"] = ins_id
                    new_instrument["symbol"] = symbol
                    new_instrument["name"] = name

                    new_instrument = StockInstrument(**new_instrument)
                    new_instrument.save()

    if bulk_update_list:
        StockInstrument.objects.bulk_update(
            objs=bulk_update_list,
            fields=["market_type", "paper_type", "ins_id", "symbol", "name"],
        )

    replace_all_arabic_letters_in_db()
