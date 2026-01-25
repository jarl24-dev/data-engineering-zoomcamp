# Data Engineering Zoomcamp – Homework 1

![Terraform](https://img.shields.io/badge/Terraform-GCP-623CE4?logo=terraform)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)

## Overview

This repository contains **Homework 1 solution** for the Data Engineering Zoomcamp

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

**Step 1:** Execute `docker run -it --rm --entrypoint=bash python:3.13`

**Step 2:** Inside the container, execute `pip --version`

**Answer:** 25.3

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- db:5432

If multiple answers are correct, select any 

**Answer:** Both postgres:5432 or db:5432 are correct, the hostname can be the name of the service or the name of the container. In case of the port '5433:5432', 5432 refers to the access to postgres inside the container, 5433 outside

## Prepare the Data

Download the green taxi trips data for November 2025:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

For this case, we create the container from de Dockerfile using the next command:

```bash
docker build -t taxi_ingest:v001 .
```

then, we execute the pipeline.py using the next docker command:

```bash
docker run -it   --network=01-docker-terraform_default   taxi_ingest:v001     --pg-user=postgres     --pg-pass=postgres     --pg-host=db     --pg-port=5432     --pg-db=ny_taxi     --target-table=green_tripdata
```

## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- 7,853
- 8,007
- 8,254
- 8,421

**Answer:** 8,007

```sql
select count(*) from green_tripdata
where lpep_pickup_datetime between '2025-11-01' and '2025-12-01'
and trip_distance <= 1.0
```

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

- 2025-11-14
- 2025-11-20
- 2025-11-23
- 2025-11-25

**Answer:** 2025-11-14

```sql
select * from green_tripdata 
where trip_distance = (select max(trip_distance) 
from green_tripdata where trip_distance <= 100)
```

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- East Harlem North
- East Harlem South
- Morningside Heights
- Forest Hills

**Answer:** East Harlem North

```sql
SELECT z."Zone", SUM(g."total_amount")
FROM green_tripdata g
INNER JOIN taxi_zone_lookup z
ON g."PULocationID" = z."LocationID"
GROUP BY z."Zone"
ORDER BY SUM(g."total_amount") DESC
LIMIT 1
```

## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's `tip` , not `trip`. We need the name of the zone, not the ID.

- JFK Airport
- Yorkville West
- East Harlem North
- LaGuardia Airport

**Answer:** Yorkville West

```sql
SELECT zdo."Zone", MAX(g."tip_amount")
FROM green_tripdata g
INNER JOIN taxi_zone_lookup zpu
ON g."PULocationID" = zpu."LocationID"
INNER JOIN taxi_zone_lookup zdo
ON g."DOLocationID" = zdo."LocationID"
WHERE zpu."Zone" = 'East Harlem North'
AND g."lpep_pickup_datetime" between '2025-11-01' and '2025-12-01'
GROUP BY zdo."Zone"
ORDER BY MAX(g."tip_amount") DESC
LIMIT 1
```

## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm

**Answer:** terraform init, terraform apply -auto-approve, terraform destroy