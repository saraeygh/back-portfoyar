import json
import requests
from rest_framework.views import APIView
from stock_market.models import CodalMonthlyActivityReport

import pandas as pd

from stock_market.tasks import get_monthly_activity_report_letter


class TestView(APIView):
    def get(self, request, *args, **kwargs):

        get_monthly_activity_report_letter()

        letters = CodalMonthlyActivityReport.objects.all()

        for letter in letters:
            if letter.has_html:
                html_url = "https://codal.ir" + letter.url

                response = requests.get(html_url, timeout=15)
                html_content = response.text

                try:
                    html_content = html_content.split("var datasource = ")[1]
                    html_content = html_content.split(";")[0]
                    json_data = json.loads(html_content)
                    letter_title_fa = json_data.get("title_Fa")
                    letter_title_en = json_data.get("title_En")
                    type = json_data.get("type")
                    period = json_data.get("period")
                    letter_period_year_end = json_data.get("periodEndToDate")
                    fin_year_end = json_data.get("yearEndToDate")
                    tracing_num = json_data.get("tracingNo")

                    sheets = json_data.get("sheets")
                    for sheet in sheets:
                        sheet_code = sheet.get("code")
                        sheet_title_fa = sheet.get("title_Fa")
                        sheet_title_en = sheet.get("title_En")
                        sheet_sequence = sheet.get("sequence")
                        sheet_alias = sheet.get("aliasName")
                        sheet_version = sheet.get("versionNo")

                        tables = sheet.get("tables")
                        for table in tables:
                            meta_table_id = table.get("metaTableId")
                            table_title_fa = table.get("title_Fa")
                            table_title_en = table.get("title_En")
                            table_sequence = table.get("sequence")
                            table_sheet_code = table.get("sheetCode")
                            table_desc = table.get("description")
                            table_alias = table.get("aliasName")
                            table_version = table.get("versionNo")

                            table_cells = table.get("cells")
                            table_df = pd.DataFrame(table_cells)
                            pass

                except Exception:
                    continue
