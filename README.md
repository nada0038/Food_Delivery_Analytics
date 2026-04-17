# Food Delivery Analytics Pipeline

**Group 2**
**Names:** Akash Nadackanal Vinod and Abijith Anil

## Project Overview

This project implements an end-to-end cloud data platform for a hypothetical food delivery service. The architecture addresses both batch data processing (for historical analytics and ML-based sentiment analysis) and real-time streaming (for immediate operational alerting on delayed orders). 

The platform utilizes Azure native services where permitted by the academic lab environment, and pivots to edge-compute alternatives where strict Azure Role-Based Access Control (RBAC) policies restricted resource provisioning.

## Final Architecture & Implementation

### Phase 1: Batch Ingestion & ETL Operations
- **Storage:** Azure Data Lake Storage Gen2 (ADLS Gen2) acts as the central data lake, containing `raw`, `cleaned`, and `curated` zones.
- **Data Generator:** A localized python script (`generate_dataset.py`) generates a synthetic dataset of 2000 historical food delivery orders (including text reviews) and uploads it directly to the `raw/` container as CSV.
- **Transformation (Azure Data Factory):** A Mapping Data Flow visually orchestrates the ETL process. It establishes connections to the Data Lake, filters out corrupted records (null Order IDs), calculates a boolean `is_delayed` derived column, and outputs a single partitioned CSV to the `cleaned/` container.

### Phase 2: AI Enrichment (Local Edge Pivot)
- **Cognitive Services:** Azure AI Language was provisioned to execute NLP sentiment analysis on customer reviews. 
- **Edge Compute Processing:** Due to standard lab subscription constraints blocking the creation of Azure Databricks Workspaces (`Microsoft.Databricks/workspaces/write` restriction), the compute layer was pivoted to a local edge processor. The `local_ai_processing.py` script pulls the cleaned data from ADLS Gen2, iterates rows against the Azure AI Language REST API to generate a `sentiment_score`, converts the dataframe to an analytics-optimized Parquet format, and pushes it to the `curated/` container.

### Phase 3: Data Warehousing Analytics (Local Edge Pivot)
- **Serverless SQL Engine:** Typical architectures employ Azure Synapse Analytics for serverless SQL querying. Due to identical RBAC lab restrictions (`Microsoft.Synapse/workspaces/write`), the warehouse execution layer was adapted to utilize DuckDB on the edge desktop. 
- **Analytics:** The `local_synapse_sql.py` script queries the raw `.parquet` file in memory, successfully executing heavy SQL aggregations that prove high delivery times heavily correlate with negative customer sentiment, while identifying underperforming service cities.

### Phase 4: Real-Time Event Streaming
- **Event Generator:** The `fake_streaming_orders.py` script continuously generates pseudo-random JSON real-time orders (simulating mobile app telemetry) and pushes them to Azure Event Hubs.
- **Event Bus:** Azure Event Hubs (Basic SKU to comply with lab policy limits) receives the high-throughput events.
- **Stream Processing:** Azure Stream Analytics hooks into the Event Hub. A continuous SQL query intercepts the stream, filtering strictly for delayed events (`is_delayed = 1`), and outputs them immediately into an ADLS Gen2 `streaming-alert/` container path partitioned dynamically by date.

## How to Test and Run the Pipeline

If you wish to test the architecture end-to-end, follow these steps sequentially:

### 1. Generate Raw Data
Run the local generation script to stage raw data in the cloud:
`python generate_dataset.py`
Verify that `food_orders.csv` lands in the `datalake/raw/` storage folder.

### 2. Execute Data Factory ETL
1. Open the Azure Data Factory Studio.
2. Navigate to the pipeline containing the Data Flow.
3. Click "Trigger Now" to run the batch ETL job.
4. Verify that `cleaned_food_data.csv` successfully lands in the `datalake/cleaned/` storage folder.

### 3. Run AI Enrichment 
1. Open terminal and run the edge processing script:
`python local_ai_processing.py`
2. Wait 1-3 minutes for the Azure AI Language model to assign sentiment scores to the dataset.
3. Verify that the highly-compressed `food_deliveries.parquet` lands in the `datalake/curated/` storage folder.

### 4. Execute Serverless SQL Analytics
Run the serverless engine locally to query the curated parquet warehouse:
`python local_synapse_sql.py`
Observe the data insights output in the terminal console indicating average delivery times partitioned by sentiment score.

### 5. Start the Real-Time Stream
1. In the Azure Portal, navigate to the Azure Stream Analytics Job and click **Start**.
2. Run the mobile-app telemetry simulator locally:
`python fake_streaming_orders.py`
3. Leave the generator running for 1-2 minutes.
4. Check the `datalake/streaming-alert/YYYY/MM/DD` folder in ADLS Gen2. You will see dynamically generated JSON files containing only the delayed orders that were actively caught from the data stream.
5. Stop the Stream Analytics Job and terminate the local Python script when finished.