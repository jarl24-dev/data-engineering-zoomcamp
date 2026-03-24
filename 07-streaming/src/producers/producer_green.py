import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from kafka import KafkaProducer
from models import RideGreen, ride_from_row_green

# Download NYC green taxi trip data (first 1000 rows)
url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
columns = ['PULocationID', 'DOLocationID', 'trip_distance', 
           'total_amount', 'lpep_pickup_datetime', 'lpep_dropoff_datetime', 
           'passenger_count', 'tip_amount']
df = pd.read_parquet(url, columns=columns)

df['lpep_pickup_datetime'] = df['lpep_pickup_datetime'].astype(str)
df['lpep_dropoff_datetime'] = df['lpep_dropoff_datetime'].astype(str)

def ride_serializer(ride):
    ride_dict = dataclasses.asdict(ride)
    json_str = json.dumps(ride_dict)
    return json_str.encode('utf-8')

server = 'localhost:9092'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=ride_serializer
)
t0 = time.time()

topic_name = 'green-trips'

for _, row in df.iterrows():
    ride = ride_from_row_green(row)
    producer.send(topic_name, value=ride)

producer.flush()

t1 = time.time()
print(f'took {(t1 - t0):.2f} seconds to process {len(df)} rows')