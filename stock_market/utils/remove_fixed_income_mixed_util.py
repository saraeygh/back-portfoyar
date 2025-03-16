from fund.models import FundInfo, UNKNOWN, FIXED_INCOME_FUND, MIXED_FUND


def remove_fixed_income_mixed(data_df):
    fixed_income_mixed = list(
        FundInfo.objects.filter(fund_type__code__in=[FIXED_INCOME_FUND, MIXED_FUND])
        .exclude(ins_code=UNKNOWN)
        .values_list("ins_code", flat=True)
    )

    data_df = data_df[~data_df["ins_code"].isin(fixed_income_mixed)]

    return data_df
