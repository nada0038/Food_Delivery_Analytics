import requests
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

# credentials
storage_account_name = "stfoodlake6536"
storage_account_key = "YOUR_STORAGE_ACCOUNT_KEY_REMOVED"
container_name = "datalake"

spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
    storage_account_key
)

cog_endpoint = "https://ai-food-language-6536.cognitiveservices.azure.com/"
cog_key = "YOUR_AI_KEY_REMOVED"

# load data
source_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/cleaned/"
df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(source_path)

df.printSchema()

# udf mapping for sentiment analysis
def get_sentiment(text):
    if not text or str(text).strip() == "":
        return "neutral"
        
    url = f"{cog_endpoint}language/:analyze-text?api-version=2022-05-01"
    headers = {
        "Ocp-Apim-Subscription-Key": cog_key,
        "Content-Type": "application/json"
    }
    
    body = {
        "kind": "SentimentAnalysis",
        "parameters": {"modelVersion": "latest"},
        "analysisInput": {
            "documents": [{"id": "1", "language": "en", "text": str(text)}]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        sentiment = result['documents'][0]['sentiment']
        return sentiment
    except Exception as e:
        return "error"

sentiment_udf = udf(get_sentiment, StringType())

df_enriched = df.withColumn("sentiment_score", sentiment_udf(col("review_text")))
df_enriched.select("Order_ID", "Delivery_Time_Minutes", "review_text", "sentiment_score").show(10, truncate=False)

# save directly to storage as parquet
output_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/curated/food_deliveries.parquet"
df_enriched.write.mode("overwrite").format("parquet").save(output_path)
