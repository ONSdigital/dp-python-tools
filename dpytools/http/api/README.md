# dpytools: APIs

## Usage

These API clients provide a set of tools for interacting with API endpoints, including uploading and managing dataset metadata.

### DatasetAPIClient

The `DatasetAPIClient` class facilitates the process of interacting with the [dp-dataset-api](https://github.com/ONSdigital/dp-dataset-api). It implements `PUT` and `POST` methods for submitting metadata to the Dataset API `/datasets/{dataset-id}/editions/{edition-id}/versions` endpoints.

A new `DatasetAPIClient` object can be created by passing `url_netloc`and `url_path` arguments:

```python
from dpytools.http.api.dataset_api_client import DatasetAPIClient

dataset_client = DatasetAPIClient(
    dataset_api_url="http://example.org/datasets"
    dataset_path="dataset-id"
    edition_path="edition-id"
)
```

#### `get_path()`

To check whether an endpoint exists within the Dataset API for a given dataset ID, use the `get_path()` method. This will return a response with an HTTP status code of 200 if the endpoint exists.

```python
response = dataset_client.get_path()

# response.status_code will be 200 if "http://example.org/datasets/dataset-id/editions/edition-id/versions" exists. Otherwise, response.status_code will be 404
```

#### `post_json()`

To submit the metadata for an **new** version of a dataset, use the `post_json()` method. This will return an HTTP status code of 201 if it is successful. Refer to the [Dataset API Swagger specification](https://github.com/ONSdigital/dp-dataset-api/blob/develop/swagger.yaml) for the required content of the `POST` request body.

```python
post_body = {
    "key1": "value1",
    "key2": "value2",
    ...
}
post_response = dataset_api_client.post_json(post_body)
```

#### `put_json()`

To update the metadata for an **existing** version of a dataset, use the `put_json()` method. This will return an HTTP status code of 200 if it is successful. Refer to the [Dataset API Swagger specification](https://github.com/ONSdigital/dp-dataset-api/blob/develop/swagger.yaml) for the required content of the `PUT` request body.

```python
put_body = {
    "key1": "value1",
    "key2": "value2",
    ...
}

put_response = dataset_api_client.put_json(put_body)
```