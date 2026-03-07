"""REST API pipeline to ingest NYC taxi data from the data engineering zoomcamp API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator


@dlt.source
def taxi_pipeline_rest_api_source():
    """
    Define dlt resources from REST API endpoints for NYC taxi data.
    
    The API endpoints are paginated with 1,000 records per page.
    Pagination stops automatically when an empty page is returned.
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "resource_defaults": {
            "write_disposition": "replace",
            "endpoint": {
                "params": {
                    "limit": 1000,
                },
                "paginator": {
                    "type": "page_number",
                    "base_page": 1,
                    "page_param": "page",
                    "total_path": None, # No total pages provided by the API
                    "stop_after_empty_page": True,
                },
            },
        },
        "resources": [
            {
                "name": "taxi_data",
                "endpoint": {
                    "path": "/",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name='taxi_pipeline',
    destination='duckdb',
    dataset_name='nyc_taxi_data',
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(taxi_pipeline_rest_api_source())
    print(load_info)  # noqa: T201
