import time
import json
import random
from azure.eventhub import EventHubProducerClient, EventData

# connection details for event hub
connection_str = 'Endpoint=sb://evh-food-analytics-6536.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_KEY_REMOVED'
eventhub_name = 'orders'

cities = ['New York', 'Chicago', 'San Francisco', 'Houston', 'Miami', 'Seattle', 'Boston']
delivery_agents = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]

def create_eventhub_producer():
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_str, 
            eventhub_name=eventhub_name
        )
        return producer
    except Exception as e:
        print("Failed to connect", e)
        return None

def generate_order_event():
    # randomly trigger delayed orders sometimes
    order_id = random.randint(100000, 999999)
    is_delayed = random.choice([0, 0, 0, 1]) 
    
    event = {
        'order_id': order_id,
        'city': random.choice(cities),
        'agent_id': random.choice(delivery_agents),
        'order_value_usd': round(random.uniform(15.0, 120.0), 2),
        'is_delayed': is_delayed,
        'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    return event

def run_simulation(producer):
    print("simulating orders... ctrl+c to cancel")
    
    try:
        while True:
            order_event = generate_order_event()
            event_json = json.dumps(order_event)
            
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(event_json))
            producer.send_batch(event_data_batch)
            
            print(f"Sent Order {order_event['order_id']} in {order_event['city']}")
            time.sleep(random.uniform(1.0, 3.0))
            
    except KeyboardInterrupt:
        print("stopped")
    finally:
        producer.close()

if __name__ == '__main__':
    producer_client = create_eventhub_producer()
    if producer_client:
        run_simulation(producer_client)
