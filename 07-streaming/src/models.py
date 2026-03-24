import json
from dataclasses import dataclass


@dataclass
class Ride:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    tpep_pickup_datetime: int  # epoch milliseconds

@dataclass
class RideGreen:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    lpep_pickup_datetime: str
    lpep_dropoff_datetime: str
    passenger_count: int
    tip_amount: float

def ride_from_row(row):
    return Ride(
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
        tpep_pickup_datetime=int(row['tpep_pickup_datetime'].timestamp() * 1000),
    )

def ride_from_row_green(row):
    return RideGreen(
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
        lpep_pickup_datetime=str(row['lpep_pickup_datetime']),
        lpep_dropoff_datetime=str(row['lpep_dropoff_datetime']),
        passenger_count=int(row['passenger_count'] if type(row['passenger_count']) == int else 0),
        tip_amount=float(row['tip_amount'])
    )

def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)

def ride_green_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return RideGreen(**ride_dict)

