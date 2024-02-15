import boto3
import json
from typing import List
from pathlib import Path

s3 = boto3.resource('s3')

def get_s3_object(object_name: str):
    """
    Given a full name, i.e "/stuff/things/file.txt return the
    object from boto3.
    """
    bucket_name, key = object_name.split("/", 1)
    s3_object = s3.Object(bucket_name, key)
    return s3_object['Body'].read()

def get_s3_object_as_dict(object_name: str) -> dict:
    """
    The above but:
    - assert its a json file
    - read it iin
    - return it as dictionary
    """
    assert object_name.endswith('.json')
    s3_object = get_s3_object(object_name)
    return json.loads(s3_object)

def download_s3_object_to_local(object_name, path):
    """
    Download a given s3 object to a local path
    """
    bucket_name, key = object_name.split('/', 1)
    s3.download_file(bucket_name, key, path)

def upload_local_file_to_s3(file: Path, object_name):
    """
    Upload something we have locally to a place on s3

    i.e a csv or json metadara file.
    """
    bucket_name, key = object_name.split('/', 1)
    s3.upload_file(str(file), bucket_name, key)

def upload_local_files_to_s3(files: List[Path], object_name):
    """
    Upload many something we have locally to a place on s3

    i.e a csv or json metadara file.
    """
    for file in files:
        assert file.exists(), f'{file} does not exist'
        upload_local_file_to_s3(file, object_name)
    
