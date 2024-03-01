# s3

## Permissions

These functions wrap the Python library [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html). As such, the functions' behaviour uses the currently active AWS permissions of the machine in question.

If you need to specify a profile (such as when developing), _all_ of the functions listed below support passing in a specific profile via the `profile_name` keyword argument.

_Note: for brevity's sake this is only demonstrated in the first example, but all functions support this pattern._

## Usage

There are five basic standalone functions for interacting with AWS S3. Each is covered in turn below.

### `get_s3_object`

In S3 terms, an object is analogous to the metadata that AWS stores about a given file, rather than the content of the file itself. The `get_s3_object` function returns a Python dictionary representation of said object.

A full description of the fields returned can be seen under `Response Syntax` [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html).

```python
from dpytools.s3.basic import get_s3_object

metadata = get_s3_object(object_name="my-bucket-name/file.txt")

# With named AWS profile
metadata = get_s3_object(
    object_name="my-bucket-name/file.txt",
    profile_name="some-profile"
)
```

Although this function returns metadata _for the most part_, the response also includes a `Body` field which can be read to get the contents of the file in question (see the next few methods for wrappers of this).

### `read_s3_file_content`

For a given object in a bucket, the `read_s3_file_content` function calls the `read()` method against it.

```python
from dpytools.s3.basic import read_s3_file_content

# Read contents of `stuff.txt` from bucket
text_file_bytes = read_s3_file_content(object_name="my-bucket/stuff.txt")

# Decode `stuff.txt` (because it's in bytes)
text_file_decoded = text_file_bytes.decode("utf-8")

# Iterate and print the lines
for line in text_file_decoded.split("\n"):
    print(line)
```

### `read_s3_file_content_as_dict`

Similar to `read_s3_file_content` but for use on JSON files. The `read_s3_file_content_as_dict` function returns a Python dictionary representation of the JSON file:

```python
from dpytools.s3.basic import read_s3_file_content_as_dict

my_dict: dict = read_s3_file_content_as_dict(object_name="my-bucket/data.json")
```

### `download_s3_file_content_to_local`

The `download_s3_file_content_to_local` function allows you to directly download a file from S3 onto your local machine.

```python
from dpytools.s3.basic import download_s3_file_content_to_local

download_s3_file_content_to_local(
    object_name="my-bucket/novel.txt",
    local_file="novel.txt"
)
```

### `upload_local_file_to_s3`

The `upload_local_file_to_s3` function allows you to upload a file from your local machine to S3.

```python
from dpytools.s3.basic import upload_local_file_to_s3

upload_local_file_to_s3(
    local_file="myfile.txt",
    object_name="my-bucket/myfile.txt"
)
```