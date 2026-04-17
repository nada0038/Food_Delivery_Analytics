import os
import duckdb
from azure.storage.blob import BlobServiceClient

# blob configs
STORAGE_KEY = "YOUR_STORAGE_ACCOUNT_KEY_REMOVED"
AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName=stfoodlake6536;AccountKey={STORAGE_KEY};EndpointSuffix=core.windows.net"

CONTAINER_NAME = "datalake"
CURATED_FILE_PATH = "curated/food_deliveries.parquet"
LOCAL_TMP_PARQUET = "food_deliveries_temp.parquet"

# fetch the parquet file locally because we cant use synapse
print("downloading parquet from data lake...")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
blob_client = container_client.get_blob_client(CURATED_FILE_PATH)

with open(LOCAL_TMP_PARQUET, "wb") as f:
    f.write(blob_client.download_blob().readall())

print("running duckdb to query data...")
conn = duckdb.connect(':memory:')

# test relation between delivery time and sentiment
query_1 = """
SELECT 
    sentiment_score as Sentiment, 
    COUNT(*) as Total_Orders,
    ROUND(AVG(Delivery_Time_Minutes), 1) as Avg_Delivery_Time_Mins
FROM read_parquet('food_deliveries_temp.parquet')
GROUP BY sentiment_score
ORDER BY Total_Orders DESC;
"""

print("Average Delivery Time effect on Sentiment")
print(conn.execute(query_1).df().to_string(index=False))

# worst cities
query_2 = """
SELECT 
    City, 
    COUNT(*) as Negative_Reviews
FROM read_parquet('food_deliveries_temp.parquet')
WHERE sentiment_score = 'Negative'
GROUP BY City
ORDER BY Negative_Reviews DESC
LIMIT 5;
"""

print("\nTop 5 Cities with Highest Negative Feedback")
print(conn.execute(query_2).df().to_string(index=False))

# cleanup to save space
if os.path.exists(LOCAL_TMP_PARQUET):
    os.remove(LOCAL_TMP_PARQUET)
