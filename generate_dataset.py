import csv
import random
from datetime import datetime, timedelta

def generate_food_dataset(num_rows=2000):
    random.seed(42)
    
    cities = ['New York', 'Chicago', 'San Francisco', 'Houston', 'Miami', 'Seattle', 'Boston']
    
    data = []
    base_time = datetime(2023, 10, 1, 12, 0, 0)
    
    for i in range(num_rows):
        order_time = base_time + timedelta(minutes=random.randint(1, 43200)) 
        
        # randomly miss some order IDs to test our pipelines
        order_id = f"ORD{random.randint(100000, 999999)}" if random.random() > 0.15 else ""
        
        delivery_time_mins = int(random.gauss(30, 15))
        delivery_time_mins = max(10, delivery_time_mins)
        
        if delivery_time_mins > 45:
            review = random.choice(["Very late and spilled.", "Terrible cold food, completely unacceptable.", "Restaurant ignored my instructions."])
        elif delivery_time_mins < 25:
            review = random.choice(["Amazing and speedy delivery!", "Super fast, piping hot!", "Driver was polite and food was hot."])
        else:
            review = random.choice([
                "Food was cold but driver was nice.",
                "Average experience, nothing special.",
                "Missing an item but otherwise fine.",
                "Driver was polite and food was hot."
            ])
            
        data.append({
            "Order_ID": order_id,
            "City": random.choice(cities),
            "Order_Date": order_time.strftime("%Y-%m-%d"),
            "Time_Ordered": order_time.strftime("%H:%M:%S"),
            "Delivery_Time_Minutes": delivery_time_mins,
            "Delivery_Person_Age": random.randint(19, 60),
            "Order_Value": round(random.uniform(15.0, 120.0), 2),
            "review_text": review
        })
        
    keys = data[0].keys()
    with open("food_orders.csv", "w", newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

if __name__ == "__main__":
    generate_food_dataset()
