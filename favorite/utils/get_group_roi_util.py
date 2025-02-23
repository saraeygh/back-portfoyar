import pandas as pd
from core.configs import STOCK_MONGO_DB, STOCK_NA_ROI
from core.utils import MongodbInterface


def get_group_roi(favorite_roi_groups):

    mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")

    group_roi = []
    for group in favorite_roi_groups:
        group_instruments = group.instruments.all()
        if group_instruments.count() < 1:
            new_group = {
                "industrial_group_id": group.id,
                "industrial_group_name": group.name,
                "daily_roi": 0,
                "weekly_roi": 0,
                "monthly_roi": 0,
                "quarterly_roi": 0,
                "half_yearly_roi": 0,
                "yearly_roi": 0,
                "three_years_roi": 0,
            }
            group_roi.append(new_group)
            continue

        group_instruments = list(
            group_instruments.values_list("instrument__ins_code", flat=True)
        )
        group_instruments = list(
            mongo_conn.collection.find(
                {"ins_code": {"$in": group_instruments}},
                {"_id": 0},
            )
        )
        group_instruments = pd.DataFrame(group_instruments)
        if group_instruments.empty:
            new_group = {
                "industrial_group_id": group.id,
                "industrial_group_name": group.name,
                "daily_roi": 0,
                "weekly_roi": 0,
                "monthly_roi": 0,
                "quarterly_roi": 0,
                "half_yearly_roi": 0,
                "yearly_roi": 0,
                "three_years_roi": 0,
            }
            group_roi.append(new_group)
            continue

        roi_list = [
            "daily_roi",
            "weekly_roi",
            "monthly_roi",
            "quarterly_roi",
            "half_yearly_roi",
            "yearly_roi",
            "three_years_roi",
        ]
        new_group = {
            "industrial_group_id": group.id,
            "industrial_group_name": group.name,
        }
        for roi in roi_list:
            filtered_df = group_instruments[(group_instruments[roi] != STOCK_NA_ROI)]
            if filtered_df.empty:
                new_group[roi] = STOCK_NA_ROI
            else:
                new_group[roi] = filtered_df[roi].mean()

        group_roi.append(new_group)

    mongo_conn.client.close()

    return group_roi
