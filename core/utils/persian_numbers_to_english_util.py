def persian_numbers_to_english(num):
    persian_numbers = "۱۲۳۴۵۶۷۸۹۰"
    english_numbers = "1234567890"

    translation_table = str.maketrans(persian_numbers, english_numbers)

    num_str = str(num)

    converted_num = num_str.translate(translation_table)

    return converted_num
