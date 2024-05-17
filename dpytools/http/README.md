# dpytools: HTTP

## Usage

### BaseHTTPClient

The `BaseHTTPClient` class standardises the process of making HTTP requests and handling the responses to those requests. If a request fails for any reason, the `BaseHTTPClient` is configured to keep retrying the request within a set time limit, depending on the value passed to the `backoff_max` argument (default value 30 seconds).

The `BaseHTTPClient` has two methods - `get()` and `post()`. These methods correspond to the `requests` library `get()` and `post()` methods, and allow you to specify optional additional arguments to be passed to the server processing the request. Instructions on the use of these methods are outlined below.

#### `get()` example

Sends a `GET` request to the specified URL with optional extra arguments.

```python
from dpytools.http.base import BaseHTTPClient

http_client = BaseHTTPClient()

response = http_client.get(url="http://example.org")
```

`response` is a `requests.Response` object, with all of the properties and methods you would expect such an object to have. For example, to view the status code of the response:

```python
print(response.status_code)
# 200
```

To view the content of the response:

```python
print(response.content)
# Prints the response content as bytes

print(response.json())
# Prints the response content as JSON
```

If the `GET` request fails for a network-related reason, this will raise an `HTTPError`.

#### `post()`

Sends a `POST` request to the specified URL with optional extra arguments.

```python
from dpytools.http.base import BaseHTTPClient

http_client = BaseHTTPClient()

response = http_client.post(url="http://example.org", *args, **kwargs)
```

As with the `get()` method, `response` is a `requests.Response` object. Since this is a `POST` request, it is likely that you would want to pass additional information to the server, which you can do using keyword arguments. For example, to pass a dictionary as JSON to the processing server:

```python
from dpytools.http.base import BaseHTTPClient

http_client = BaseHTTPClient()

dictionary_to_pass = {
    "key1": "value1",
    "key2": "value2"
}
response = http_client.post(
    url="http://example.org",
    json=dictionary_to_pass
)
```

If the `POST` request fails for a network-related reason, this will raise an `HTTPError`.

### UploadServiceClient

The `UploadServiceClient` class facilitates the process of uploading a file to the [dp-upload-service](https://github.com/ONSdigital/dp-upload-service). It implements methods for uploading CSV and SDMX files to the DP Upload Service. Which method you use will depend on whether you are accessing the `/upload` or `upload-new` endpoint. Details on using each method are provided below.

A new `UploadServiceClient` object can be created by passing an `upload_url`:

```python
from dpytools.http.upload import UploadServiceClient

upload_client = UploadServiceClient(upload_url="http://example.org/upload")
```

There are two potential mechanisms for auth. 

1. **Service account auth** - set the env var `SERVICE_TOKEN_FOR_UPLOAD` with the token.

2. **User auth** - set the env vars `FLORENCE_USER`, `FLORENCE_PASSWORD` and `IDENTITY_API_URL`.

The distinction is to allow authorised users to run the upload client from their local machines where required. 

#### upload_csv() and upload_sdmx()

To upload files to the `/upload` endpoint use the `upload_csv()` and `upload_sdmx()` methods. These methods accept the path to the file and an optional chunk size with a default value of 5242880 bytes (5MB).

```python
from dpytools.http.upload import UploadServiceClient

upload_client = UploadServiceClient("http://example.org/upload")


upload_client.upload_csv("path/to/file.csv")

upload_client.upload_sdmx("path/to/file.sdmx")

upload_client.upload_sdmx("path/to/file.sdmx", chunk_size=1000)
```

#### upload_new_csv() and upload_new_sdmx()

To upload files to the `/upload-new` endpoint, use the `upload_new_csv()` and `upload_new_sdmx()` methods. These methods accept the path to the file and an optional chunk size with a default value of 5242880 bytes (5MB).

The `/upload-new` endpoint also requires an `alias_name` and `title` to be provided in the HTTP request parameters. If these are not explicitly stated in the method call, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension.

```python
from dpytools.http.upload import UploadServiceClient

upload_client = UploadServiceClient("http://example.org/upload-new")

# `alias_name` and `title` arguments not provided, so these values will default to `file.csv` and `file` respectively.
upload_client.upload_new_csv(
    "path/to/file.csv",)

# `alias_name` and `title` arguments provided, so these values will be set explicitly.
upload_client.upload_new_sdmx(
    "path/to/file.sdmx",
    alias_name="my-awesome-file.sdmx",
    title="My Awesome SDMX File"
)
```
