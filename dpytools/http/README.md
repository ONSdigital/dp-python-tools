# dpytools: HTTP

## Usage

### BaseHTTPClient

The `BaseHTTPClient` class standardises the process of making HTTP requests and handling the responses to those requests. If a request fails for any reason, the `BaseHTTPClient` is configured to keep retrying the request within a set time limit, depending on the value passed to the `backoff_max` argument (default value 30 seconds).

The `BaseHTTPClient` has two methods - `get()` and `post()`. These methods correspond to the `requests` library `get()` and `post()` methods, and allow you to specify optional additional arguments to be passed to the server processing the request. Instructions on the use of these methods are outlined below.

### `get()` example

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

### `post()`

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