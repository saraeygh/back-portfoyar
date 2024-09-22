from django.contrib import admin
from stock_market.models import StockInstrument
from stock_market.utils import MAIN_MARKET_TYPE_DICT, ALL_PAPER_TYPE_DICT


@admin.register(StockInstrument)
class StockInstrumentAdmin(admin.ModelAdmin):
    autocomplete_fields = ("industrial_group",)

    list_display = (
        "id",
        "industrial_group",
        "market_type_name",
        "paper_type_name",
        "ins_code",
        "ins_id",
        "symbol",
        "name",
    )

    list_display_links = (
        "id",
        "industrial_group",
        "market_type_name",
        "paper_type_name",
        "ins_id",
        "symbol",
        "name",
    )

    list_filter = ("market_type", "paper_type")

    ordering = ("-updated_at",)

    search_fields = ("id", "industrial_group__name", "symbol", "name", "ins_code")

    @admin.display(description="نوع بازار")
    def market_type_name(self, obj: StockInstrument):
        market_type_num = obj.market_type
        market_type_name = MAIN_MARKET_TYPE_DICT.get(market_type_num)
        return market_type_name

    @admin.display(description="نوع اوراق")
    def paper_type_name(self, obj: StockInstrument):
        paper_type_num = obj.paper_type
        paper_type_name = ALL_PAPER_TYPE_DICT.get(paper_type_num)
        return paper_type_name
