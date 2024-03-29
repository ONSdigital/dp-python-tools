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

### UploadClient

The `UploadClient` class facilitates the process of uploading a file to an AWS S3 bucket by splitting the file into chunks and transmitting these chunks individually. This is done via the `upload()` method.

A new `UploadClient` object can be created by passing an `upload_url`:

```python
from dpytools.http.upload import UploadClient

upload_client = UploadClient(upload_url="http://example.org/upload")
```

To access the DP Upload Service, a Florence access control token must be provided. For security purposes this should be set using an environment variable.

#### upload()

The `UploadClient` provides an `upload()` method which accepts a file to be uploaded, an S3 Bucket identifier, a Florence access token, and an optional chunk size (default value 5242880 bytes).

The S3 Bucket identifier should be set as an environment variable. The Florence access token should be generated via the DP Identity API and passed as an argument to `upload()`.

Calling the `upload()` method creates the temporary file chunks, uploads these to the `UploadClient.upload_url`, and finally deletes the temporary files. The method returns the S3 Object key and S3 URI of the Object's location:

```python
from dpytools.http.upload import UploadClient

upload_client = UploadClient("http://example.org/upload")

s3_bucket = os.getenv("S3_BUCKET")
florence_access_token = "<florence-access-token-here>"

s3_key, s3_uri = upload_client.upload(
    "path/to/countries.csv",
    s3_bucket,
    florence_access_token,
)

# The s3_key is a unique identifier, and consists of the timestamp of when the upload process commenced and the filename of the uploaded file:
# s3_key example: "110324094616-countries-csv"

# The s3_uri concatenates the s3_bucket and s3_key values:
# s3_uri example: "s3://mybucket/110324094616-countries-csv"
```
