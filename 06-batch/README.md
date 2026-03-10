# Module 6 Homework

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the Yellow 2025-11 data from the official website:

```bash
!sh -c "mkdir -p data/raw/yellow/2025/11/ && curl -o data/raw/yellow/2025/11/yellow_tripdata_2025-11.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet"
```

## Question 1: Install Spark and PySpark

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.

What's the output?

> [!NOTE]
> To install PySpark follow this [guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/06-batch/setup/)

### Solution:

```pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

print(f"Spark version: {spark.version}")
```

**Answer:** Spark version: 4.1.1


## Question 2: Yellow November 2025

Read the November 2025 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- 25MB
- 75MB
- 100MB

### Solution:

```pyspark
year = 2025
month = 11

input_path = f'data/raw/yellow/{year}/{month:02d}/'
output_path = f'data/pq/yellow/{year}/{month:02d}/'

df = spark.read.parquet(input_path)

df = df.repartition(4)

df.write.parquet(output_path, mode="overwrite")
```

```bash
!sh -c "ls -lh data/pq/yellow/2025/11/*.parquet"
```

**Answer:** 25MB

## Question 3: Count records

How many taxi trips were there on the 15th of November?

Consider only trips that started on the 15th of November.

- 62,610
- 102,340
- 162,604
- 225,768

### Solution:

```pyspark
from pyspark.sql.functions import to_date

df_repartitioned = spark.read \
        .option("header", "true") \
        .parquet("data/pq/yellow/2025/11/")
df_repartitioned.filter(to_date(df_repartitioned.tpep_pickup_datetime) == "2025-11-15").count()
```

**Answer:** 162,604

## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

- 22.7
- 58.2
- 90.6
- 134.5

### Solution:

```pyspark
from pyspark.sql.functions import unix_timestamp, round, max

df_repartitioned\
    .withColumn("trip_duration", \
                round((unix_timestamp("tpep_dropoff_datetime")-unix_timestamp("tpep_pickup_datetime")) /3600 , 2)) \
    .select(max("trip_duration")).show()
```

**Answer:** 90.6

## Question 5: User Interface

Spark's User Interface which shows the application's dashboard runs on which local port?

- 80
- 443
- 4040
- 8080

**Answer:** 4040

## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```bash
!sh -c "mkdir -p data/raw/misc && curl -o data/raw/misc/taxi_zone_lookup.csv https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
```

Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

- Governor's Island/Ellis Island/Liberty Island
- Arden Heights
- Rikers Island
- Jamaica Bay

If multiple answers are correct, select any

### Solution:

```pyspark
df_yellow = spark.read \
        .option("header", "true") \
        .parquet("data/pq/yellow/2025/11/")

df_zones = spark.read \
        .option("header", "true") \
        .csv("data/raw/misc/")

from pyspark.sql.functions import col

df_join = df_repartitioned.alias('trips') \
    .join(df_zones.alias('zones'), 
          col('trips.PULocationID') == col('zones.LocationID'), 'left')\
    .select("trips.*", "zones.Zone")
# Ahora puedes seleccionar usando el alias
df_join.groupBy("Zone").count().orderBy(col("count").asc()).limit(5).toPandas()
```

**Answer:** Governor's Island/Ellis Island/Liberty Island or Arden Heights

## Submitting the solutions

- Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw6
- Deadline: See the website


## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

Read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

### Example post for LinkedIn

```
🚀 Week 6 of Data Engineering Zoomcamp by @DataTalksClub complete!

Just finished Module 6 - Batch Processing with Spark. Learned how to:

✅ Set up PySpark and create Spark sessions
✅ Read and process Parquet files at scale
✅ Repartition data for optimal performance
✅ Analyze millions of taxi trips with DataFrames
✅ Use Spark UI for monitoring jobs

Processing 4M+ taxi trips with Spark - distributed computing is powerful! 💪

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X

```
⚡ Module 6 of Data Engineering Zoomcamp done!

- Batch processing with Spark 🔥
- PySpark & DataFrames
- Parquet file optimization
- Spark UI on port 4040

My solution: <LINK>

Free course by @DataTalksClub: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```