from tqdm import tqdm

# from favorite.models import OptionsFavoriteSymbol
from stock_market.models import StockIndustrialGroup, StockInstrument


def replace_arabic_letters(string):
    string = string.replace("ي", "ی")
    string = string.replace("ك", "ک")

    return string


def replace_all_arabic_letters_in_db():
    # fo_bulk_list = []
    # favorite_options = OptionsFavoriteSymbol.objects.all()
    # for favorite_option in tqdm(favorite_options, desc="Favorite options", ncols=10):
    #     favorite_option.symbol = replace_arabic_letters(favorite_option.symbol)
    #     fo_bulk_list.append(favorite_option)
    # OptionsFavoriteSymbol.objects.bulk_update(objs=fo_bulk_list, fields=["symbol"])

    ig_bulk_list = []
    industrial_groups = StockIndustrialGroup.objects.all()
    for industrial_group in tqdm(industrial_groups, desc="Industrial Groups", ncols=10):
        industrial_group.name = replace_arabic_letters(industrial_group.name)
        ig_bulk_list.append(industrial_group)
    StockIndustrialGroup.objects.bulk_update(objs=ig_bulk_list, fields=["name"])

    si_bulk_list = []
    instruments = StockInstrument.objects.all()
    for instrument in tqdm(instruments, desc="Instruments", ncols=10):
        instrument.symbol = replace_arabic_letters(instrument.symbol)
        instrument.name = replace_arabic_letters(instrument.name)
        si_bulk_list.append(instrument)
    StockInstrument.objects.bulk_update(objs=si_bulk_list, fields=["symbol", "name"])


def replace_arabic_letters_pd(row, column_name):
    name = str(row.get(column_name))
    name = replace_arabic_letters(name)

    return name
