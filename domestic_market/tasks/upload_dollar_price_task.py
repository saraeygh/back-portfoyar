import os

import jdatetime
import pandas as pd
from core.utils import send_upload_error_file_email
from domestic_market.models import DomesticDollarPrice
from domestic_market.serializers import UploadDollarPriceSerializer
from samaneh.settings import BASE_DIR


def upload_dollar_price(dollar_prices_list_of_dicts) -> None:
    error_dollar_prices = []
    dollar_prices_bulk_list = []

    for dollar_price in dollar_prices_list_of_dicts:
        print(f"Dollar price: {dollar_price}", end="\r")

        dollar_price_srz = UploadDollarPriceSerializer(data=dollar_price)
        if dollar_price_srz.is_valid():
            try:
                existing_dollar_price = DomesticDollarPrice.objects.get(
                    date=dollar_price_srz.validated_data["date"]
                )
                dollar_price_exists = True

            except DomesticDollarPrice.DoesNotExist:
                dollar_price_exists = False

            if dollar_price_exists:
                dollar_price_srz.validated_data.pop("date")
                for key, value in dollar_price_srz.validated_data.items():
                    setattr(existing_dollar_price, key, value)
                existing_dollar_price.save()

            else:
                new_dollar_price = DomesticDollarPrice(
                    date=dollar_price_srz.validated_data["date"],
                    date_shamsi=str(
                        jdatetime.date.fromgregorian(
                            date=dollar_price_srz.validated_data["date"]
                        )
                    ),
                    nima=dollar_price_srz.validated_data["nima"],
                    azad=dollar_price_srz.validated_data["azad"],
                )
                dollar_prices_bulk_list.append(new_dollar_price)

        else:
            for field, error_list in dollar_price_srz.errors.items():
                errors = []
                for error in error_list:
                    error_str = str(error)
                    errors.append(error_str)

                dollar_price["error_" + field] = errors

            error_dollar_prices.append(dollar_price)

    print("")

    if dollar_prices_bulk_list:
        DomesticDollarPrice.objects.bulk_create(dollar_prices_bulk_list)

    if error_dollar_prices:
        error_dollar_prices_df = pd.DataFrame(error_dollar_prices)

        save_dir = f"{BASE_DIR}/media/uploaded_files/"
        is_dir = os.path.isdir(save_dir)
        if not is_dir:
            os.makedirs(save_dir)

        file_name = "error_dollar_price.csv"
        file_path = save_dir + file_name

        error_dollar_prices_df.to_csv(file_path, index=False)
        send_upload_error_file_email(file_path=file_path, task_name="قیمت‌های دلار")
