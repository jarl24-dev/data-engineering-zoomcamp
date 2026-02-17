# Module 4 Homework: Analytics Engineering with dbt

In this homework, we'll use the dbt project in `04-analytics-engineering/taxi_rides_ny/` to transform NYC taxi data and answer questions by querying the models.

## Setup

1. Set up your dbt project following the [setup guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/setup)
2. Load the Green and Yellow taxi data for 2019-2020 into your warehouse
3. Run `dbt build --target prod` to create all models and run tests

> **Note:** By default, dbt uses the `dev` target. You must use `--target prod` to build the models in the production dataset, which is required for the homework queries below.

After a successful build, you should have models like `fct_trips`, `dim_zones`, and `fct_monthly_zone_revenue` in your warehouse.

---

### Question 1. dbt Lineage and Execution

Given a dbt project with the following structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `dbt run --select int_trips_unioned`, what models will be built?

- `stg_green_tripdata`, `stg_yellow_tripdata`, and `int_trips_unioned` (upstream dependencies)
- Any model with upstream and downstream dependencies to `int_trips_unioned`
- `int_trips_unioned` only
- `int_trips_unioned`, `int_trips`, and `fct_trips` (downstream dependencies)

**Answer:** `int_trips_unioned` only

---

### Question 2. dbt Tests

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data.

What happens when you run `dbt test --select fct_trips`?

- dbt will skip the test because the model didn't change
- dbt will fail the test, returning a non-zero exit code
- dbt will pass the test with a warning about the new value
- dbt will update the configuration to include the new value

**Answer:** dbt will fail the test, returning a non-zero exit code

---

### Question 3. Counting Records in `fct_monthly_zone_revenue`

After running your dbt project, query the `fct_monthly_zone_revenue` model.

What is the count of records in the `fct_monthly_zone_revenue` model?

- 12,998
- 14,120
- 12,184
- 15,421

### Solution:

```SQL
SELECT COUNT(*) FROM `<PROJECT_ID>.dbt_prod.fct_monthly_zone_revenue`;
```

**Answer:** 12,184

---

### Question 4. Best Performing Zone for Green Taxis (2020)

Using the `fct_monthly_zone_revenue` table, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

Which zone had the highest revenue?

- East Harlem North
- Morningside Heights
- East Harlem South
- Washington Heights South

### Solution:

```SQL
SELECT pickup_zone,revenue_month, revenue_monthly_total_amount 
FROM `<PROJECT_ID>.dbt_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green' AND EXTRACT(YEAR FROM revenue_month) = 2020
ORDER BY revenue_monthly_total_amount DESC LIMIT 1;
```

**Answer:** East Harlem North

---

### Question 5. Green Taxi Trip Counts (October 2019)

Using the `fct_monthly_zone_revenue` table, what is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

- 500,234
- 350,891
- 384,624
- 421,509

### Solution:

```SQL
SELECT SUM(total_monthly_trips)
FROM `<PROJECT_ID>.dbt_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green' AND revenue_month = '2019-10-01';
```

**Answer:** 384,624

---

### Question 6. Build a Staging Model for FHV Data

Create a staging model for the **For-Hire Vehicle (FHV)** trip data for 2019.

1. Load the [FHV trip data for 2019](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv) into your data warehouse
2. Create a staging model `stg_fhv_tripdata` with these requirements:
   - Filter out records where `dispatching_base_num IS NULL`
   - Rename fields to match your project's naming conventions (e.g., `PUlocationID` → `pickup_location_id`)

What is the count of records in `stg_fhv_tripdata`?

- 42,084,899
- 43,244,693
- 22,998,722
- 44,112,187

### Solution:

1. Execute `load_fhv_trip_data.py` to load data into our GCP bucket:

```bash
uv run python load_fhv_trip_data.py
```

2. Load data from the bucket to Bigquery:

```SQL
CREATE OR REPLACE EXTERNAL TABLE `<PROJECT_ID>.nytaxi.external_fhv_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://<BUCKET_NAME>/fhv/2019/*.csv.gz'
  ],
  compression = 'GZIP',
  skip_leading_rows = 1
);

CREATE OR REPLACE TABLE `<PROJECT_ID>.nytaxi.fhv_tripdata`
AS
SELECT * FROM `<PROJECT_ID>.nytaxi.external_fhv_tripdata`;;
```

3. Modify the source.yml file adding the new table:

```yaml
      - name: fhv_tripdata
        columns:
          - name: dispatching_base_num
            description: identifier 
          - name: pickup_datetime
            description: Date and time when the meter was engaged
          - name: dropOff_datetime
            description: Date and time when the meter was disengaged
          - name: PUlocationID
            description: TLC Taxi Zone where the meter was engaged	
          - name: DOlocationID
            description: TLC Taxi Zone where the meter was disengaged
          - name: SR_Flag
            description: integer number flag
          - name: Affiliated_base_number
            description: Identifier
```

4. Create `stg_fhv_tripdata.sql` inside the staging directory:

```SQL
with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (

    select
        -- identifiers
        cast(dispatching_base_num as string) as dispatching_base_num,
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,
        cast(affiliated_base_number as string) as affiliated_base_number,

        --timestamp
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropoff_datetime as timestamp) as dropoff_datetime,

        -- trip info
        cast(sr_flag as string) as sr_flag
    from source
    WHERE dispatching_base_num IS NOT NULL
)

select * from renamed;
```

5. Execute the next command on dbt to load data into the development dataset:

```bash
dbt build --select +stg_fhv_tripdata
```

6. Verify that data was loaded into the development dataset on Bigquery and then execute the next query:

```SQL
SELECT COUNT(*)  FROM `<PROJECT_ID>.<DEVELOPMENT_DATASET>.stg_fhv_tripdata`
```

---

## Submitting the solutions

- Form for submitting: <https://courses.datatalks.club/de-zoomcamp-2026/homework/hw4>

=======

## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

Read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

### Example post for LinkedIn

```
🚀 Week 4 of Data Engineering Zoomcamp by @DataTalksClub complete!

Just finished Module 4 - Analytics Engineering with dbt. Learned how to:

✅ Build transformation models with dbt
✅ Create staging, intermediate, and fact tables
✅ Write tests to ensure data quality
✅ Understand lineage and model dependencies
✅ Analyze revenue patterns across NYC zones

Transforming raw data into analytics-ready models - the T in ELT!

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X

```
📈 Module 4 of Data Engineering Zoomcamp done!

- Analytics Engineering with dbt
- Transformation models & tests
- Data lineage & dependencies
- NYC taxi revenue analysis

My solution: <LINK>

Free course by @DataTalksClub: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```