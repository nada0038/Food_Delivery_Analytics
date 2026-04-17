# Setup for Azure Food Delivery Capstone
$rgName = "rg-food-delivery"
$location = "eastus"
$suffix = Get-Random -Minimum 1000 -Maximum 9999
$stName = "stfoodlake$suffix"
$evhName = "evh-food-analytics-$suffix"
$adfName = "adf-food-analytics-$suffix"

Write-Host "Creating Resource Group: $rgName in $location"
az group create --name $rgName --location $location -o none

Write-Host "Creating Storage Account: $stName"
az storage account create --name $stName --resource-group $rgName --location $location --sku Standard_LRS --enable-hierarchical-namespace true -o none

Write-Host "Creating Storage Containers & Folders"
$key = (az storage account keys list -g $rgName -n $stName --query "[0].value" -o tsv)
az storage fs create -n datalake --account-name $stName --account-key $key -o none
az storage fs directory create -n raw -f datalake --account-name $stName --account-key $key -o none
az storage fs directory create -n cleaned -f datalake --account-name $stName --account-key $key -o none
az storage fs directory create -n curated -f datalake --account-name $stName --account-key $key -o none
az storage fs directory create -n streaming-output -f datalake --account-name $stName --account-key $key -o none

Write-Host "Uploading food_orders.csv to raw data lake container"
az storage fs file upload -s "food_orders.csv" -p "raw/food_orders.csv" -f datalake --account-name $stName --account-key $key -o none

Write-Host "Creating Data Factory: $adfName"
az datafactory factory create --resource-group $rgName --factory-name $adfName --location $location -o none

Write-Host "Creating Event Hubs Namespace: $evhName"
az eventhubs namespace create --name $evhName --resource-group $rgName --location $location --sku Standard -o none

Write-Host "Creating Event Hub 'orders'"
az eventhubs eventhub create --name orders --namespace-name $evhName --resource-group $rgName --message-retention 1 --partition-count 2 -o none

Write-Host ""
Write-Host "========================================="
Write-Host "PROVISIONING SUCCESSFUL (Phase 1)"
Write-Host "Resource Group: $rgName"
Write-Host "Storage Account Name: $stName"
Write-Host "Data Factory Name: $adfName"
Write-Host "Event Hub Namespace: $evhName"
Write-Host "Dataset successfully uploaded to raw/food_orders.csv"
Write-Host "========================================="
