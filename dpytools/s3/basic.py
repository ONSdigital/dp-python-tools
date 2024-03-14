import json
import tarfile
import tempfile
from pathlib import Path
from typing import Optional, Union

import boto3


def _get_s3_client(profile_name):
    client = boto3.Session(profile_name=profile_name).client("s3")
    return client


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
    if not isinstance(local_file, Path):
        local_file = Path(local_file)

    assert local_file.exists(), f"The file {local_file.absolute()} does not exist."
    client = _get_s3_client(profile_name)

    boto3.setup_default_session(profile_name=profile_name)
    bucket_name, key = object_name.split("/", 1)
    with open(local_file) as f:
        client.put_object(Body=f.read(), Bucket=bucket_name, Key=key)


def decompress_s3_tar(
    object_name: str, directory: Union[str, Path], profile_name: Optional[str] = None
):
    """
    Given a url to an s3 object that is a tar file, decompress it
    to the provided directory path.
    """

    if not object_name.endswith(".tar"):
        raise NotImplementedError(
            f"This function currently only handles archives using the tar extension. Got {object_name}"
        )

    if isinstance(directory, str):
        directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    bucket_name = object_name.split("/")[0]
    object_key = "/".join(object_name.split("/")[1:])

    tmp_file = tempfile.NamedTemporaryFile()
    with open(tmp_file.name, "wb") as f:
        client = _get_s3_client(profile_name)
        client.download_fileobj(bucket_name, object_key, f)

    # Decompress all the files to the directory specified.
    with tarfile.open(tmp_file.name, mode="r:*") as tar:
        tar.extractall(directory.absolute())
