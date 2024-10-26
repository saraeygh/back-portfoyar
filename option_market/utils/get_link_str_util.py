def get_link_str(row, col_name):
    ime_link = "https://cdn.ime.co.ir/"
    try:
        code = str(row.get(col_name))
        if len(code) < 10:
            return ime_link
        link = f"https://www.tsetmc.com/instInfo/{code}"

    except Exception:
        link = ime_link

    return link
