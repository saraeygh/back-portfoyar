import os
import pandas as pd
from core.utils import send_upload_error_file_email
from django.core.files.storage import default_storage
from global_market.utils import get_commodity_type_dict
from global_market.models import GlobalRelation
from stock_market.models import StockInstrument
from tqdm import tqdm
from samaneh.settings.common import BASE_DIR


def get_comm_types_dict():
    comm_types_dict = get_commodity_type_dict()
    comm_types = {}
    for name_industry, type_id in comm_types_dict.items():
        comm_types[name_industry[0]] = type_id

    return comm_types


def get_symbol_code_dict(excel_file):
    code_df = pd.read_excel(io=excel_file, sheet_name="code")
    code_df = code_df.drop_duplicates(subset=["code"], keep="first")
    code_df = code_df.to_dict(orient="records")
    symbol_code_dict = {}
    for item in code_df:
        symbol_code_dict[item["symbol"]] = item["code"]

    return symbol_code_dict


def get_comm_type_id(column_rows, comm_types):
    column_rows = column_rows.dropna()
    column_rows = column_rows.to_dict()
    comm_type = column_rows.pop(0)
    comm_type_id = comm_types.get(comm_type)

    return comm_type, comm_type_id, column_rows


def delete_prev_relations(comm_type_id):
    prev_relations = GlobalRelation.objects.filter(
        global_commodity_type_id=comm_type_id
    )
    prev_relations.delete()

    return


def upload_xlsx_relation_task(excel_file_name: str) -> None:

    file_path = f"{BASE_DIR}/media/uploaded_files/{excel_file_name}"
    with default_storage.open(file_path) as excel_file:
        symbol_code_dict = get_symbol_code_dict(excel_file)
        relation_df = pd.read_excel(io=excel_file, sheet_name="relation")

    error_list_of_dict = []
    comm_types = get_comm_types_dict()
    for _, column_rows in tqdm(relation_df.items(), desc="Relation", ncols=10):
        comm_type_bulk_list = []
        comm_type, comm_type_id, column_rows = get_comm_type_id(column_rows, comm_types)
        if comm_type_id is None:
            error_list_of_dict.append({"comm_type": comm_type, "comm_type_id": ""})
            continue

        delete_prev_relations(comm_type_id)

        for _, symbol in column_rows.items():
            ins_code = symbol_code_dict.get(symbol)
            try:
                instrument = StockInstrument.objects.get(ins_code=ins_code)
            except StockInstrument.DoesNotExist:
                error_list_of_dict.append({"symbol": symbol, "ins_code": ins_code})
                continue

            new_relation = GlobalRelation(
                global_commodity_type_id=comm_type_id,
                stock_instrument_id=instrument.id,
            )
            comm_type_bulk_list.append(new_relation)

        if comm_type_bulk_list:
            GlobalRelation.objects.bulk_create(comm_type_bulk_list)

    if error_list_of_dict:
        error_list_df = pd.DataFrame(error_list_of_dict)

        save_dir = f"{BASE_DIR}/media/uploaded_files/"
        is_dir = os.path.isdir(save_dir)
        if not is_dir:
            os.makedirs(save_dir)

        file_name = "error_relation.csv"
        file_path = save_dir + file_name
        error_list_df.to_csv(file_path, index=False)

        send_upload_error_file_email(
            file_path=file_path, task_name="ارتباط بازار جهانی"
        )
