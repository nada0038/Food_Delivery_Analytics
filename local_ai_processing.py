import os
import requests
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient

# set up keys
STORAGE_KEY = "YOUR_STORAGE_ACCOUNT_KEY_REMOVED"
AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName=stfoodlake6536;AccountKey={STORAGE_KEY};EndpointSuffix=core.windows.net"
AI_ENDPOINT = "https://ai-food-language-6536.cognitiveservices.azure.com/language/:analyze-text?api-version=2022-05-01"
AI_KEY = "YOUR_AI_KEY_REMOVED"

CONTAINER_NAME = "datalake"
CLEANED_FILE_PATH = "cleaned/cleaned_food_data.csv"
CURATED_FILE_PATH = "curated/food_deliveries.parquet"

# pull raw csv from data lake
print("getting data from lake...")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

blob_client = container_client.get_blob_client(CLEANED_FILE_PATH)
download_stream = blob_client.download_blob()
df = pd.read_csv(BytesIO(download_stream.readall()))

# run NLP analysis
print(f"analyzing {len(df)} rows with azure language services...")
headers = {
    "Ocp-Apim-Subscription-Key": AI_KEY,
    "Content-Type": "application/json"
}

def get_sentiment(text):
    if not isinstance(text, str) or not text.strip():
        return "Neutral"
    
    payload = {
        "kind": "SentimentAnalysis",
        "parameters": {"modelVersion": "latest"},
        "analysisInput": {
            "documents": [{"id": "1", "language": "en", "text": str(text)}]
        }
    }
    
    try:
        response = requests.post(AI_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["results"]["documents"][0]["sentiment"].capitalize()
    except Exception as e:
        return "Neutral"

sentiments = []
for idx, row in df.iterrows():
    if idx % 100 == 0:
        print(f"analyzed {idx} records")
    sentiments.append(get_sentiment(row['review_text']))

df['sentiment_score'] = sentiments

print(df[['Order_ID', 'review_text', 'sentiment_score']].head(8))

# push to curated folder as parquet
print("converting to parquet and uploading...")
parquet_data = df.to_parquet(index=False)

curated_blob_client = container_client.get_blob_client(CURATED_FILE_PATH)
curated_blob_client.upload_blob(parquet_data, overwrite=True)

print("done")
