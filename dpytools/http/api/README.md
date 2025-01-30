# dpytools: APIs

## Usage

These API clients provide a set of tools for interacting with API endpoints, including uploading and managing dataset metadata.

### DatasetAPIClient

The `DatasetAPIClient` class facilitates the process of interacting with the [dp-dataset-api](https://github.com/ONSdigital/dp-dataset-api). It implements `PUT` and `POST` methods for submitting metadata to the Dataset API `/datasets/{dataset-id}` endpoints.

A new `DatasetAPIClient` object can be created by passing `url_netloc`and `url_path` arguments:

```python
from dpytools.http.api.dataset_api_client import DatasetAPIClient

dataset_client = DatasetAPIClient(
    url_netloc="http://example.org/datasets"
    url_path="dataset-id"
)
```

#### `get_path()`

To check whether an endpoint exists within the Dataset API for a given dataset ID, use the `get_path()` method. This will return a response with an HTTP status code of 200 if the endpoint exists.

```python
response = dataset_client.get_path()

# response.status_code will be 200 if "http://example.org/datasets/dataset-id" exists. Otherwise, response.status_code will be 404
```

#### `put_json()`

To update the metadata for an **existing** dataset, use the `put_json()` method. This will return an HTTP status code of 200 if it is successful.

```python
put_body = {
    "_id": "dataset-id",
    "state": "associated",
    "type": "cantabular_flexible_table",
    "contacts": [
        {"name": "sarah"}
    ],
    "description": "description text here",
    "keywords": [],
    "methodologies": [],
    "national_statistic": False,
    "publications": [],
    "qmi": {
        "description": "QMI description", 
        "href": "QMI link", 
        "title": "QMI title"
    },
    "related_datasets": [],
    "title": "this is a dataset",
}
with open("post.json", "rb") as f:
    put_body_json = json.load(f)

put_response = dataset_api_client.put_json(put_body_json)
```

#### `post_json()`

To submit the metadata for an **new** dataset, use the `post_json()` method. This will return an HTTP status code of 201 if it is successful.

```python
post_body = {
    "_id": "dataset-id",
    "next": {
        "_id": "dataset-id",
        "links": {
            "editions": {"href": "http://example.org/datasets/dataset-id/editions"},
            "self": {"href": "http://example.org/datasets/dataset-id"},
        },
        "state": "created",
        "type": "cantabular_flexible_table",
    },
}
with open("post.json", "rb") as f:
    post_body_json = json.load(f)

post_response = dataset_api_client.post_json(post_body_json)
```

