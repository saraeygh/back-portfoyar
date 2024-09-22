from stock_market.models import CodalMonthlyActivityReport


def get_existing_tracing_number_set():
    existing_tracing_number_set = set(
        CodalMonthlyActivityReport.objects.values_list("tracing_number", flat=True)
    )

    return existing_tracing_number_set
