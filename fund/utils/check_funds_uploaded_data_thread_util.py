from io import BytesIO
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from colorama import Fore, Style

import pandas as pd


from django.core.files.storage import default_storage
from samaneh.settings import BASE_DIR

from core.utils import replace_arabic_letters
from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)


from stock_market.models import StockInstrument

from fund.models import FundInfo


def get_excel_file(excel_file_name):
    with default_storage.open(
        f"{BASE_DIR}/media/uploaded_files/{excel_file_name}"
    ) as file:
        excel_file = file.read()

    return excel_file


SHEETS = {
    "funds": "funds",
    "portfo": "portfo",
    "buy_sell": "buy_sell",
}


def check_funds_sheet(db_funds, excel_file):
    xslx_funds = pd.read_excel(io=BytesIO(excel_file), sheet_name=SHEETS["funds"])

    funds_error = []
    for ـ, row in xslx_funds.iterrows():
        fund_name = replace_arabic_letters(row.get("fund").strip())

        matched_funds = 0
        for fund_info_obj in db_funds:
            if fund_info_obj.name in fund_name:
                matched_funds += 1

        if matched_funds != 1:
            row = row.to_dict()
            row["matched_funds"] = matched_funds
            funds_error.append(row)

    funds_error = pd.DataFrame(funds_error)

    send_upload_error_file_email(
        error_df=funds_error, task_name="اطلاعات صندوق‌ها", sheet_name=SHEETS["funds"]
    )


def check_portfo_sheet(excel_file):
    xslx_symbols = pd.read_excel(io=BytesIO(excel_file), sheet_name=SHEETS["portfo"])
    xslx_symbols = xslx_symbols.drop_duplicates(subset="symbol", keep="first")

    symbols_error = []
    for _, row in xslx_symbols.iterrows():
        symbol = replace_arabic_letters(row.get("symbol").strip())

        matched_instrument = StockInstrument.objects.filter(symbol=symbol).count()
        if matched_instrument != 1:
            matched_instrument = StockInstrument.objects.filter(name=symbol).count()
            if matched_instrument != 1:
                row = row.to_dict()
                row["matched_instrument"] = matched_instrument
                symbols_error.append(row)

    symbols_error = pd.DataFrame(symbols_error)

    send_upload_error_file_email(
        error_df=symbols_error, task_name="اطلاعات نمادها", sheet_name=SHEETS["portfo"]
    )


def check_funds_uploaded_data_thread(excel_file_name: str):

    excel_file = get_excel_file(excel_file_name)
    db_funds = FundInfo.objects.all()

    check_funds_sheet(db_funds, excel_file)

    check_portfo_sheet(excel_file)


def send_upload_error_file_email(
    error_df: pd.DataFrame, task_name: str, sheet_name: str
):
    if error_df.empty:
        return

    print(Fore.BLUE + "Sending invalid records email" + Style.RESET_ALL)

    save_dir = f"{BASE_DIR}/media/uploaded_files/"
    is_dir = os.path.isdir(save_dir)
    if not is_dir:
        os.makedirs(save_dir)

    file_name = f"error_df_{sheet_name}.xlsx"
    file_path = save_dir + file_name
    error_df.to_excel(file_path, index=False, sheet_name=sheet_name)

    subject = f"نتیجه آپلود اکسل {task_name}"

    html_body = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>
            <p style='direction: rtl; unicode-bidi: embed;'>
            "مواردی که در فایل سی‌اس‌وی پیوست آمده‌اند،"
            "را اصلاح و مجدد آپلود کنید."
            </p>
        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_name}",
    )

    message.attach(part)

    text = message.as_string()

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_TO, text)
    except Exception as e:
        print(Fore.RED + f"Error sending email: {e}" + Style.RESET_ALL)

    try:
        os.remove(file_path)
    except Exception:
        print(Fore.RED + f"Error removing file: {e}" + Style.RESET_ALL)
