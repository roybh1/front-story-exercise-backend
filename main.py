import pandas as pd
from datetime import datetime
import pytz
import dateparser

eastern = pytz.timezone("US/Eastern")

try:
    cost = pd.read_csv("./cost_1.csv")
except Exception as e:
    cost = pd.read_csv("https://s3.amazonaws.com/frontstory-test-data/server-side/cost_1.csv")

try:
    revenue = pd.read_csv("./revenue_1.csv")
except Exception as e:
    revenue = pd.read_csv("https://s3.amazonaws.com/frontstory-test-data/server-side/revenue_1.csv")

def convert_est_to_utc(val):
    d = dateparser.parse(val)
    return (d.replace(tzinfo=eastern).astimezone(pytz.utc))

def main(date_from, date_to, cost = None, revenue = None):
    date_from = dateparser.parse(date_from)
    date_to = dateparser.parse(date_to)

    #Convert tz
    cost["data_date"] = cost["data_date"].map(convert_est_to_utc)
    revenue["data_date"] = revenue["data_date"].map(convert_est_to_utc)

    #join to one df
    df = pd.merge(cost,revenue, on = ["data_date", "campaign_id"])

    #calc rev per click
    uv_col = df.apply(lambda row: float(row.revenue) / row.clicks if row.clicks != 0 else None, axis=1)
    cpc_col = df.apply(lambda row: float(row.cost) / row.clicks if row.clicks != 0 else None, axis=1)
    df = df.assign(uv=uv_col.values, cpc=cpc_col.values)
    roi_col = df.apply(lambda row: float(row.uv) / row.cpc if row.cpc is not None and row.cpc != 0 else None, axis=1)
    profit_col = df.apply(lambda row: row.revenue - row.cost, axis=1)
    df = df.assign(roi=roi_col.values, profit=profit_col.values)

    #aggregate daily per campaign
    ##FOR some reason this throws an exception, I couldn't figure it out in time --> "Series has no attribute data_date" but it does print it...
    print(df.columns)
    day_col = df.apply(lambda row: dateparser.parse(row.data_date).date())
    df = df.assign(day=day_col.values)
    grouped_mean = df.groupby(["day", "campaign_id"]).mean()
    grouped_sum = df.groupby(["day", "campaign_id"]).sum()
    new_df = pd.DataFrame()
    new_df = new_df.assign(
        id = grouped_mean["campaign_id"],
        name= grouped_mean["campaign_name"],
        total_rev=grouped_sum["revenue"],
        total_cost=grouped_sum["cost"],
        total_profit=grouped_sum["profit"],
        total_roi=grouped_sum["roi"],
        avg_uv=grouped_mean["uv"],
        avg_cpc=grouped_mean["cpc"]
    )
    print(new_df)
    return new_df



