from celery_singleton import Singleton

import json
import jdatetime
from tqdm import trange

from django.utils import timezone

from samaneh.celery import app

from core.utils import get_http_response, run_main_task
from core.configs import FA_TO_EN_TRANSLATION_TABLE


from stock_market.utils import get_company_from_codal, get_existing_tracing_number_set
from stock_market.models import CodalMonthlyActivityReport

HEADERS = {
    "Host": "search.codal.ir",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://codal.ir",
    "Connection": "keep-alive",
    "Referer": "https://codal.ir/",
    "Sec-Fetch-Site": "same-site",
}


def get_number_of_pages():
    URL = (
        "https://search.codal.ir/api/search/v2/"
        "q?&Audited=true&AuditorRef=-1&Category=-1&Childs=true"
        "&CompanyState=-1&CompanyType=-1&Consolidatable=true"
        "&IsNotAudited=false&Length=-1&LetterType=58&Mains=true"
        "&NotAudited=true&NotConsolidatable=true&PageNumber=1"
        "&Publisher=false&TracingNo=-1&search=true"
    )

    page_number = get_http_response(req_url=URL, req_headers=HEADERS)

    try:
        page_number = page_number.json()
        page_number = page_number["Page"]
    except Exception:
        page_number = 1

    return page_number


def get_gregorian_date_time(jalali_date_time_str: str):
    output_text = jalali_date_time_str.translate(FA_TO_EN_TRANSLATION_TABLE)
    output_text = output_text.replace(" ", "/")
    output_text = output_text.replace(":", "/")
    year, month, day, hour, minute, second = map(int, output_text.split("/"))

    date_time = jdatetime.datetime(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second
    )
    date_time = date_time.togregorian()
    date_time = timezone.make_aware(date_time)
    return date_time


def get_monthly_activity_report_letter_main():

    company_dict = get_company_from_codal()
    existing_tracing_number_set = get_existing_tracing_number_set()

    PAGES = get_number_of_pages()
    tracing_number_repeatation = 0
    for page in trange(1, PAGES):
        URL = (
            "https://search.codal.ir/api/search/v2/"
            "q?&Audited=true&AuditorRef=-1&Category=-1&Childs=true"
            "&CompanyState=-1&CompanyType=-1&Consolidatable=true"
            "&IsNotAudited=false&Length=1&LetterType=58&Mains=true"
            f"&NotAudited=true&NotConsolidatable=true&PageNumber={page}"
            "&Publisher=false&TracingNo=-1&search=true"
        )

        letters = get_http_response(req_url=URL, req_headers=HEADERS)

        try:
            letters = letters.json()
            letters = letters["Letters"]
        except Exception:
            letters = []

        stock_month_report_bulk = []
        for letter in letters:
            tracing_number = letter["TracingNo"]
            stock_month_report = {}
            company = company_dict.get(letter["Symbol"])
            if not company:
                continue
            elif tracing_number in existing_tracing_number_set:
                tracing_number_repeatation += 1
                continue
            else:
                sent_date_time = letter["SentDateTime"]
                sent_date_time = get_gregorian_date_time(sent_date_time)
                publish_date_time = letter["PublishDateTime"]
                publish_date_time = get_gregorian_date_time(publish_date_time)

                stock_month_report["company"] = company
                stock_month_report["tracing_number"] = tracing_number
                stock_month_report["under_supervision"] = letter["UnderSupervision"]
                stock_month_report["title"] = letter["Title"]
                stock_month_report["code"] = letter["LetterCode"]
                stock_month_report["sent_date_time"] = sent_date_time
                stock_month_report["publish_date_time"] = publish_date_time
                stock_month_report["has_html"] = letter["HasHtml"]
                stock_month_report["is_estimate"] = letter["IsEstimate"]
                stock_month_report["url"] = letter["Url"]
                stock_month_report["has_excel"] = letter["HasExcel"]
                stock_month_report["has_pdf"] = letter["HasPdf"]
                stock_month_report["has_xbrl"] = letter["HasXbrl"]
                stock_month_report["has_attachment"] = letter["HasAttachment"]
                stock_month_report["attachment_url"] = letter["AttachmentUrl"]
                stock_month_report["pdf_url"] = letter["PdfUrl"]
                stock_month_report["excel_url"] = letter["ExcelUrl"]
                stock_month_report["xbrl_url"] = letter["XbrlUrl"]
                stock_month_report["supervision"] = json.dumps(
                    letter.pop("SuperVision")
                )
            existing_tracing_number_set.add(tracing_number)
            new_report = CodalMonthlyActivityReport(**stock_month_report)
            stock_month_report_bulk.append(new_report)

            if len(stock_month_report_bulk) > 100:
                CodalMonthlyActivityReport.objects.bulk_create(stock_month_report_bulk)
                stock_month_report_bulk = []

        if stock_month_report_bulk:
            CodalMonthlyActivityReport.objects.bulk_create(stock_month_report_bulk)

        if tracing_number_repeatation > 200:
            break


@app.task(base=Singleton, name="get_monthly_activity_report_letter_task")
def get_monthly_activity_report_letter():

    run_main_task(
        main_task=get_monthly_activity_report_letter_main,
        daily=True,
    )
