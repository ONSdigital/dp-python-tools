import json
import tempfile
from pathlib import Path
from typing import List, Optional, Union

import boto3


def _get_s3_client(profile_name: str | None = None):
    return boto3.Session(profile_name=profile_name).client("s3")

def get_s3_object(object_name: str, profile_name: Optional[str] = None) -> dict:
    """
    Given an s3 object identifier, i.e "my-bucket/things/file.txt" returns a dictionary which
    is the boto3 aws representation of an s3 object.

    Please see "Response Syntax" here:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
    """
    client = _get_s3_client(profile_name)
    bucket_name, key = object_name.split("/", 1)
    return client.get_object(Bucket=bucket_name, Key=key)


def read_s3_file_content(object_name: str, profile_name: Optional[str] = None) -> bytes:
    """
    Given an s3 object identifer, i.e "my-bucket/things/file.txt" fetches then read()'s
    the body (content) of s3 object (file).
    """
    s3_object = get_s3_object(object_name, profile_name=profile_name)
    return s3_object["Body"].read()


def read_s3_file_content_as_dict(
    object_name: str, profile_name: Optional[str] = None
) -> dict:
    """
    Given an s3 object identifer for a json file, i.e "my-bucket/things/file.json"
    fetches the content of the file as a python dictionary.
    """
    if not object_name.endswith(".json"):
        raise ValueError("Object name must end with '.json'")
    s3_file_content = read_s3_file_content(object_name, profile_name=profile_name)
    return json.loads(s3_file_content.decode("utf-8"))


def download_s3_file_content_to_local(
    object_name: str, local_file: str, profile_name: Optional[str] = None
):
    """
    Download the file represented by a given s3 object to the local path provided
    """
    s3_file_content = read_s3_file_content(object_name, profile_name=profile_name)
    with open(local_file, "w") as f:
        f.write(s3_file_content.decode("utf-8"))


def upload_local_file_to_s3(
    local_file: Union[str, Path], object_name: str, profile_name: Optional[str] = None
):
    """
    Uploads the provided file from local to s3 as the provided object name.
    """
    bucket_name, key = object_name.split("/", 1)
    return upload_local_file_to_s3_exact(local_file, bucket_name, key, profile_name)


def upload_local_file_to_s3_exact(
    local_file: Union[str, Path],
    bucket_name: str,
    object_key: str,
    profile_name: Optional[str] = None,
):
    """
    Uploads the provided file from local file-system to an S3 bucket

    Args:
        local_file: The path of the local file to upload
        bucket_name: The name of the S3 bucket to upload to
        object_key: The object key of the file to create
        profile_name: Optional AWS profile name to use for session
    """
    if not isinstance(local_file, Path):
        local_file = Path(local_file)

    assert local_file.exists(), f"The file {local_file.absolute()} does not exist."
    client = _get_s3_client(profile_name)

    boto3.setup_default_session(profile_name=profile_name)
    with open(local_file) as f:
        client.put_object(Body=f.read(), Bucket=bucket_name, Key=object_key)


def s3_folder_recieved(
    object_name: str, directory: Union[str, Path], profile_name: Optional[str] = None
):
    """
    Given a url to an s3 object a folder contaning files,
    download content to provided directory path.
    """
    if isinstance(directory, str):
        directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    bucket_name = object_name.split("/")[0]
    object_key = "/".join(object_name.split("/")[1:])

    client = _get_s3_client(profile_name)
    list_objects = client.list_objects_v2(Bucket=bucket_name, Prefix=object_key)

    tmp_file = tempfile.NamedTemporaryFile()
    with open(tmp_file.name, "wb") as f:
        for c in list_objects["Contents"]:
            if c["Key"].startswith(object_key) and not c["Key"].endswith("/"):
                client.download_fileobj(bucket_name, c["Key"], f)

    for c in list_objects["Contents"]:
        if c["Key"].startswith(object_key) and not c["Key"].endswith("/"):
            filename = c["Key"].split("/")[1]
            client.download_file(
                bucket_name, c["Key"], Filename=str(directory) + "/" + filename
            )


def move_s3_object(bucket_name: str, origin_object_key: str, target_object_key: str):
    """
    Copy a file on S3 bucket to another location, then delete the original file.

    Args:
        origin_object_key: Key of the object to copy
        target_object_key: Where to move the file to
    """
    client = _get_s3_client()

    client.copy_object(
        Bucket=bucket_name,
        Key=target_object_key,
        CopySource={"Bucket": bucket_name, "Key": origin_object_key},
    )

    client.delete_object(Bucket=bucket_name, Key=origin_object_key)


def list_keys_in_path(bucket_name: str, path: str) -> List[str]:
    """
    Get all keys for all objects in an S3 bucket that start with the given path.

    Args:
        bucket_name: Bucket to retrieve files under
        path: Key prefix to filter by

    """
    client = _get_s3_client()
    list_objects = client.list_objects_v2(Bucket=bucket_name, Prefix=path)

    if list_objects is None or "Contents" not in list_objects:
        return []
    
    return [content["Key"] for content in list_objects["Contents"]]
