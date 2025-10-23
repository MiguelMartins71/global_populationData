from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import FloatType

# Inicializa a Spark session
spark = SparkSession.builder.appName("TransformationsGlobalETL").getOrCreate()

# Leitura dos dados já tratados no estágio de exploration
df_global = spark.read.table("workspace.default.global_population_stats")
# === 1️⃣ Padronização de colunas ===
df_global = (
    df_global
    .withColumnRenamed("Country", "country")
    .withColumnRenamed("Population(in millions)", "population_millions")
    .withColumnRenamed("Area (km2)", "area_km2")
    
)

# === 2️⃣ Limpeza básica ===
df_global = (
    df_global
    .withColumn("country", f.trim(f.upper(f.col("country"))))
    .dropDuplicates(["country"])
)

# === 3️⃣ Tratamento de valores nulos ===
df_global = (
    df_global
    .fillna({"population_millions": 0, "area_km2": 0, "gdp_billions": 0})
)

# === 4️⃣ Cálculo de densidade populacional ===
df_global = df_global.withColumn(
    "population_density",
    (f.col("population_millions") * 1_000_000 / f.col("area_km2")).cast(FloatType())
)



# === 6️⃣ Ranking dos 10 países mais populosos ===
df_top_population = (
    df_global
    .orderBy(f.col("population_millions").desc())
    .limit(10)
)



# === 8️⃣ Grava as saídas em camadas prata e ouro ===
df_global.write.mode("overwrite").parquet("/mnt/data/silver/global_cleaned")
df_top_population.write.mode("overwrite").parquet("/mnt/data/gold/top10_population")
df_top_gdp.write.mode("overwrite").parquet("/mnt/data/gold/top10_gdp")

print("Transformações concluídas com sucesso 🚀")
