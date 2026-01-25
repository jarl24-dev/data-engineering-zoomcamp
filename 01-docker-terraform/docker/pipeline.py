import click
import pandas as pd
import pyarrow.parquet as pq
import fsspec
from sqlalchemy import create_engine

@click.command()
@click.option('--pg-user', default='postgres', help='PostgreSQL user')
@click.option('--pg-pass', default='postgres', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5433, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default='green_tripdata', help='Target table name')
@click.option('--chunksize', default=10000, type=int, help='Chunk size for reading CSV')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    """Ingest NYC taxi green trip data into PostgreSQL database."""
    prefix = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
    url = f'{prefix}/green_tripdata_{year}-{month:02d}.parquet'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    # Opening file with pyarrow directly from URL
    with fsspec.open(url) as f:
        parquet_file = pq.ParquetFile(f)

        # Iteramos sobre los lotes sin haber descargado el archivo completo manualmente
        for batch in parquet_file.iter_batches(batch_size=10000):
            df_chunk = batch.to_pandas()
            df_chunk.to_sql(name='green_tripdata', con=engine, if_exists='append')
            #print(f"Procesando {len(df_chunk)} filas desde la nube...")

    url_lookup = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
    df_lookup = pd.read_csv(url_lookup)
    df_lookup.to_sql(name='taxi_zone_lookup', con=engine, if_exists='append')

if __name__ == '__main__':
    run()
