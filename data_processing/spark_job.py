import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth, round, lag, when, coalesce, lit
from pyspark.sql.window import Window

def run_p1_pipeline(input_path: str, output_path: str):
    spark = SparkSession.builder \
        .appName("P1_Trend_Analysis_Industrial") \
        .getOrCreate()

    # 1. Chargement
    df_raw = spark.read.csv(input_path, header=True, inferSchema=True)

    # 2. Nettoyage et préservation des ~50 000+ lignes
    df_clean = df_raw.select(
        col("Product"),
        col("Brand"),
        col("Price").cast("double"),
        col("Dispatch Date").cast("date").alias("SaleDate"),
        col("Quantity Sold").cast("int").alias("Quantity"),
        col("Region"),
        col("RAM"),
        col("ROM")
    ).dropna(subset=["SaleDate", "Quantity", "Price", "Brand"])

    # 3. Enrichissement temporel précis au jour près
    df_prepared = df_clean \
        .withColumn("Year", year(col("SaleDate"))) \
        .withColumn("Month", month(col("SaleDate"))) \
        .withColumn("Day", dayofmonth(col("SaleDate"))) \
        .withColumn("Revenue", round(col("Price") * col("Quantity"), 2))

    # 4. Windowing sans agrégation destructrice
    window_spec = Window.partitionBy("Brand").orderBy("SaleDate")

    df_final = df_prepared \
        .withColumn("Prev_Quantity", coalesce(lag("Quantity", 1).over(window_spec), lit(0))) \
        .withColumn("Growth_Rate_%", 
            round(((col("Quantity") - col("Prev_Quantity")) / when(col("Prev_Quantity") == 0, 1).otherwise(col("Prev_Quantity"))) * 100, 2)
        ) \
        .withColumn("Trend", 
            when(col("Growth_Rate_%") > 10, "Forte Hausse")
            .when((col("Growth_Rate_%") <= 10) & (col("Growth_Rate_%") >= -5), "Stable")
            .when(col("Growth_Rate_%") < -5, "Baisse")
            .otherwise("Nouvelle / N/A")
        )

    # 5. Exportation CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.toPandas().to_csv(output_path, index=False)
    print(f"Pipeline P1 exécuté avec succès : {output_path}")

if __name__ == "__main__":
    run_p1_pipeline("data/raw/mobile_sales_data.csv", "data/processed/cleaned_data.csv")