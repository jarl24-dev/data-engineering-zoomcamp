""" @bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: vendor_id
    type: integer
    description: Taxi technology provider ID
  - name: pickup_datetime
    type: timestamp
    description: Timestamp when meter was engaged
  - name: dropoff_datetime
    type: timestamp
    description: Timestamp when meter was disengaged
  - name: pickup_location_id
    type: integer
    description: TLC Taxi Zone where trip started
  - name: dropoff_location_id
    type: integer
    description: TLC Taxi Zone where trip ended
  - name: passenger_count
    type: integer
    description: Number of passengers
  - name: trip_distance
    type: float
    description: Trip distance in miles
  - name: rate_code_id
    type: integer
    description: Rate code
  - name: store_and_fwd_flag
    type: string
    description: Trip record stored in vehicle memory
  - name: payment_type
    type: integer
    description: Payment method code
  - name: fare_amount
    type: float
    description: Time and distance fare
  - name: extra
    type: float
    description: Miscellaneous extras and surcharges
  - name: mta_tax
    type: float
    description: MTA tax
  - name: tip_amount
    type: float
    description: Tip amount
  - name: tolls_amount
    type: float
    description: Total tolls paid
  - name: improvement_surcharge
    type: float
    description: Improvement surcharge
  - name: total_amount
    type: float
    description: Total amount charged
  - name: congestion_surcharge
    type: float
    description: Congestion surcharge
  - name: taxi_type
    type: string
    description: Type of taxi (yellow/green)
  - name: extraction_date
    type: timestamp
    description: Timestamp when the data was extracted

@bruin """

import os
# FORZAR ESTO ANTES DE QUE NADA SE CARGUE
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"

try:
    import tzdata
    import os
    # Esto le dice a las librerías de C++ (como PyArrow) dónde está la DB
    os.environ["PYARROW_TZDATA_PATH"] = os.path.join(os.path.dirname(tzdata.__file__), "zoneinfo")
except ImportError:
    pass

import pandas as pd
import os
import json
from datetime import datetime

def materialize():
    # Load environment variables
    start_date_str = os.getenv("BRUIN_START_DATE")
    
    # Parse date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    year = start_date.year
    month = start_date.month
    
    # Load pipeline variables
    vars_str = os.getenv("BRUIN_VARS", "{}")
    pipeline_vars = json.loads(vars_str)
    taxi_types = pipeline_vars.get("taxi_types", ["yellow"])
    
    dfs = [] 
    
    for taxi_type in taxi_types:
        # Construct URL for the specific month
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
        print(f"Downloading data from: {url}")
        
        try:
            df = pd.read_parquet(url)
            
            # Normalize columns to snake_case and standard names
            df.columns = [c.lower() for c in df.columns]
            
            rename_map = {
                'tpep_pickup_datetime': 'pickup_datetime',
                'tpep_dropoff_datetime': 'dropoff_datetime',
                'lpep_pickup_datetime': 'pickup_datetime',
                'lpep_dropoff_datetime': 'dropoff_datetime',
                'vendorid': 'vendor_id',
                'ratecodeid': 'rate_code_id',
                'pulocationid': 'pickup_location_id',
                'dolocationid': 'dropoff_location_id',
            }
            df = df.rename(columns=rename_map)

            # ELIMINAR ZONA HORARIA PARA EVITAR ERROR EN WINDOWS
            if 'pickup_datetime' in df.columns:
                df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime']).dt.tz_localize(None)
            if 'dropoff_datetime' in df.columns:
                df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime']).dt.tz_localize(None)
            
            # Add metadata
            df['taxi_type'] = taxi_type
            df['extraction_date'] = datetime.now().replace(tzinfo=None)
            
            dfs.append(df)
            
        except Exception as e:
            print(f"Warning: Could not download or process {url}. Error: {e}")
            continue

    if not dfs:
        print("No data found for this window.")
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)
