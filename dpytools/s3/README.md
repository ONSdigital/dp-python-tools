# s3

## Permissions

These functions wrap the python library [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) as such the behaviour is to use the currently active aws permissions of the machine in question.

If you wish/need/want to specify a profile (such as when developing) you can do so as _all_ of the functions listed support the passing in of a specific profile via the `profile_name` keyword argument.

_Note: for brevities sake I'll ony show this in the first example, but all the functions support this pattern._

## Usage

This module contains five basic stand alione functions for interacting with aws s3, each will be covered in turn:

### get_s3_object

An "object" in s3 terms is more analagous to metadata that aws stores about a given file rather than being the file itself. This function retuns a dictionary representation of said object.

A full description of the fields returned can be seen under `Response Syntax` [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html).

```python
from dpytool.s3 import get_s3_object

metadata = get_s3_object("my-bucket-name/file.txt")

# With named aws profile
metadata = get_s3_object("my-bucket-name/file.txt", profile_name="some-profile")
```

Although this is metadata _for the most part_, it does include a "Body" field which can be read to get the contents of the file in question (see next few methods for wrappers of this).

### read_s3_file_content

For a given file in a bucket, this function fetches calls the `read()` method against it.

Simple example usage for reading a text file follows:

```python
from dpytools.s3.basic import read_s3_file_content

# Read contents of text file from bucket
text_file_bytes = read_s3_file_content("my-bucket/stuff.txt")

# Decode it (because its in bytes)
text_file_decoded = text_file_bytes.decode("utf-8")

# Iterate and print the lines
for line in text_file_decoded.split("\n"):
    print(line)
```

### read_s3_file_content_as_dict

Similar to the above but for use on json files - this automatically returns the python dictionary representation of same:

```python
from dpytools.s3.basic import read_s3_file_content_as_dict

my_dict: dict = read_s3_file_content_as_dict("my-bucket/data.json")
```

### download_s3_file_content_to_local

Allows you to directly download a file from s3 onto your local machine.

```python
from dpytools.s3.basic import download_s3_file_content_to_local

download_s3_file_content_to_local("my-bucket/novel.txt", "novel.txt")
```

### upload_local_file_to_s3

Allows you to upload a file from your local machine to s3.

```python
from dpytools.s3.basic import upload_local_file_to_s3

upload_local_file_to_s3("myfile.txt", "my-bucket/myfile.txt")
```