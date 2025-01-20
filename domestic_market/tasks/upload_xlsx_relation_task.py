import os
import pandas as pd
from tqdm import tqdm

from django.core.files.storage import default_storage

from samaneh.settings import BASE_DIR
from core.utils import send_upload_error_file_email

from domestic_market.models import DomesticProducer, DomesticRelation
from stock_market.models import StockInstrument


def upload_xlsx_relation(excel_file_name: str):

    file_path = f"{BASE_DIR}/media/uploaded_files/{excel_file_name}"
    with default_storage.open(file_path) as excel_file:
        relation_df = pd.read_excel(io=excel_file, sheet_name="relation")

    error_list_of_dict = []
    domestic_relation_bulk_list = []
    for _, row in tqdm(relation_df.iterrows(), desc="Relation", ncols=10):
        try:
            ime_code = int(row.get("ime_code", 0))
            ins_code = str(row.get("ins_code", 0))

            domestic_producer = DomesticProducer.objects.get(code=ime_code)
            stock_instrument = StockInstrument.objects.get(ins_code=ins_code)
            domestic_relation = DomesticRelation.objects.filter(
                domestic_producer=domestic_producer, stock_instrument=stock_instrument
            )
            if (
                domestic_producer
                and stock_instrument
                and not domestic_relation.exists()
            ):
                domestic_relation = DomesticRelation(
                    domestic_producer=domestic_producer,
                    stock_instrument=stock_instrument,
                )
                domestic_relation_bulk_list.append(domestic_relation)
        except Exception as e:
            error_list_of_dict.append(
                {
                    "ime_code": row.get("ime_code"),
                    "ime_producer": row.get("ime_producer"),
                    "ins_code": row.get("ins_code"),
                    "stock_name": row.get("stock_name"),
                    "stock_symbol": row.get("stock_symbol"),
                    "error": str(e),
                }
            )
            continue

    if domestic_relation_bulk_list:
        DomesticRelation.objects.bulk_create(domestic_relation_bulk_list)

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
            file_path=file_path,
            task_name="ارتباط بازار داخلی",
            filename=excel_file_name,
        )
