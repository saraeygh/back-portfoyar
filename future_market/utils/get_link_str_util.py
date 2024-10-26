def get_link_str(row, col_name):
    try:
        link = int(row.get(col_name))
        link = f"https://www.tsetmc.com/instInfo/{row.get(col_name)}"
    except Exception:
        link = "https://cdn.ime.co.ir/"

    return link
