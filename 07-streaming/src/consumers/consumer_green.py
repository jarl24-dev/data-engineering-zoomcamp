import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from kafka import KafkaConsumer
from models import ride_green_deserializer

server = 'localhost:9092'
topic_name = 'green-trips'

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='postgres',
    user='postgres',
    password='postgres'
)
conn.autocommit = True
cur = conn.cursor()

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],

    auto_offset_reset='earliest',
    group_id='rides-to-postgres',
    value_deserializer=ride_green_deserializer
)

print(f"Listening to {topic_name} and writing to PostgreSQL...")

count = 0
for message in consumer:
    ride = message.value
    cur.execute(
        """INSERT INTO green_processed_events
           (PULocationID, DOLocationID, trip_distance, total_amount, pickup_datetime, dropoff_datetime, passenger_count, tip_amount)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (ride.PULocationID, ride.DOLocationID,
         ride.trip_distance, ride.total_amount, ride.lpep_pickup_datetime, ride.lpep_dropoff_datetime, ride.passenger_count, ride.tip_amount)
    )
    count += 1
    if count % 100 == 0:
        print(f"Inserted {count} rows...")

consumer.close()
cur.close()
conn.close()