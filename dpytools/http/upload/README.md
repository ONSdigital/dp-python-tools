# dpytools: Upload

## Usage

### BaseUploadClient

The `BaseUploadClient` class extends the `BaseHTTPClient` class by adding `upload_url` and `TokenAuth` properties to the base class. It has one abstract method, `upload()`, which any child class must implement.

### UploadServiceClient

The `UploadServiceClient` class facilitates the process of uploading a file to the [dp-upload-service](https://github.com/ONSdigital/dp-upload-service). It implements methods for uploading files to the DP Upload Service `/upload` and `/upload-new` endpoints. Details on using each method are provided below.

A new `UploadServiceClient` object can be created by passing an `upload_url` argument:

```python
from dpytools.http.upload.upload_service_client import UploadServiceClient

upload_client = UploadServiceClient(upload_url="http://example.org/upload")
```

There are two potential mechanisms for authorisation: 

1. **Service account auth** - set the env var `SERVICE_TOKEN_FOR_UPLOAD` with the token.

2. **User auth** - set the env vars `FLORENCE_USER`, `FLORENCE_PASSWORD` and `IDENTITY_API_URL`.

The distinction is to allow authorised users to run the client from their local machines where required. 

#### upload()

To upload files to the `/upload` endpoint use the `upload()` method. This method accepts the path to the file, the mimetype to be used in the HTTP request parameters, and an optional chunk size with a default value of 5242880 bytes (5MB).

```python
from dpytools.http.upload.upload_service_client import UploadServiceClient

upload_client = UploadServiceClient("http://example.org/upload")

# Upload a CSV file
upload_client.upload(
    filepath="path/to/file.csv",
    mimetype="text/csv"
)

# Upload an XML file
upload_client.upload(
    filepath="path/to/file.xml",
    mimetype="application/xml"
)

# Upload an XML file with a chunk size of 1000 bytes
upload_client.upload(
    filepath="path/to/file.xml",
    mimetype="application/xml",
    chunk_size=1000
)
```

#### upload_new()

To upload files to the `/upload-new` endpoint, use the `upload_new()` method. This method accepts the path to the file, the mimetype to be used in the HTTP request parameters, and an optional chunk size with a default value of 5242880 bytes (5MB).

The `/upload-new` endpoint also requires a number of parameters to be provided in the HTTP request. If these are not explicitly stated in the method call, the following default values will be set:

| Parameter      | Default                                                                     | Type    |
|:---------------|:----------------------------------------------------------------------------|:--------|
| alias_name     | filename with the extension                                                 | String  |
| title          | filename without the extension                                              | String  |
| is_publishable | False                                                                       | Boolean |
| license        | "Open Government Licence v3.0"                                              | String  |
| license_url    | "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" | String  |
| collection_id  | "collection-id"                                                             | String  |

```python
from dpytools.http.upload.upload_service_client import UploadServiceClient

upload_client = UploadServiceClient("http://example.org/upload-new")

# Optional arguments not provided, so these will default to the values specified in the table above
upload_client.upload_new(
    file_path="path/to/file.csv",
    mimetype="text/csv"
)

# `alias_name`, `title` and `collection_id` arguments provided, so these values will be set explicitly.
upload_client.upload_new(
    file_path="path/to/file.xml",
    mimetype="application/xml"
    alias_name="my-awesome-file.xml",
    title="My Awesome SDMX File",
    collection_id="my-collection-id"
)
```
