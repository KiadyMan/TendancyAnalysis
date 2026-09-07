import pandas as pd
from backend.models.trend import Trend

CLEANED_DATA_PATH = "data/processed/cleaned_data.csv"


async def refresh_trends():
    """Relit la sortie de P1 (spark_job.py) et la pousse dans Mongo."""
    df = pd.read_csv(CLEANED_DATA_PATH, parse_dates=["SaleDate"])

    await Trend.delete_all()

    docs = [
        Trend(
            product=row.get("Product"),
            brand=row["Brand"],
            price=row["Price"],
            sale_date=row["SaleDate"].date(),
            quantity=int(row["Quantity"]),
            region=row.get("Region"),
            ram=row.get("RAM"),
            rom=row.get("ROM"),
            revenue=row["Revenue"],
            prev_quantity=int(row["Prev_Quantity"]),
            growth_rate_pct=row["Growth_Rate_%"],
            trend=row["Trend"],
        )
        for _, row in df.iterrows()
    ]
    if docs:
        await Trend.insert_many(docs)

    return len(docs)


async def get_all_trends(limit: int = 1000):
    return await Trend.find_all().limit(limit).to_list()


async def get_trends_by_brand(brand: str, limit: int = 1000):
    return await Trend.find(
        Trend.brand == brand
    ).limit(limit).to_list()