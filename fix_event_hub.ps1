$rgName = "rg-food-delivery"
$location = "eastus"
$evhName = "evh-food-analytics-6536"

Write-Host "Creating Event Hub Namespace with Basic SKU to comply with CloudLabs policy..."
az eventhubs namespace create --name $evhName --resource-group $rgName --location $location --sku Basic -o none

Write-Host "Creating Event Hub named 'orders'..."
az eventhubs eventhub create --name orders --namespace-name $evhName --resource-group $rgName --partition-count 2 -o none

# Retrieve connection string securely
$connStr = (az eventhubs namespace authorization-rule keys list --resource-group $rgName --namespace-name $evhName --name RootManageSharedAccessKey --query "primaryConnectionString" -o tsv)

Write-Host ""
Write-Host "=================="
Write-Host "Event Hub is FIXED and READY!"
Write-Host "Your Event Hub Connection String (Update fake_streaming_orders.py with this):"
Write-Host $connStr
Write-Host "=================="
