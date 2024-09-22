import jdatetime


def convert_int_date_to_str_date(row, date_col_name):
    date = str(row.get(date_col_name))
    year, month, day = int(date[0:4]), int(date[4:6]), int(date[6:])

    date = jdatetime.GregorianToJalali(gyear=year, gmonth=month, gday=day)
    year, month, day = date.jyear, date.jmonth, date.jday

    date = f"{year}/{month}/{day}"

    return date
