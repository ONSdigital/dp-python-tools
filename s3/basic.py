import boto3
import json
import logging
from typing import List
from pathlib import Path

def setup_session(profile_name: str):
    boto3.setup_default_session(profile_name=profile_name)
    return boto3.resource('s3')

s3 = setup_session('dp-bleed-dev')

def get_s3_object(s3, object_name: str):
    """
    Given a full name, i.e "/stuff/things/file.txt return the
    object from boto3.
    """
    try:
        bucket_name, key = object_name.split("/", 1)
        s3_object = s3.Object(bucket_name, key)
        object_data = s3_object.get()
        return object_data['Body'].read()
    except Exception as e:
        logging.error(f"Error getting S3 object: {e}")
        return None

def get_s3_object_as_dict(s3, object_name: str) -> dict:
    """ 
    The above but:
    - assert its a json file
    - read it in
    - return it as dictionary
    """
    if not object_name.endswith('.json'):
        raise ValueError("Object name must end with '.json'")
    s3_object = get_s3_object(s3, object_name)
    return json.loads(s3_object)

def download_s3_object_to_local(s3, object_name: str, local_path: str):
    """
    Download a given s3 object to a local path
    """
    try:
        bucket_name, key = object_name.split('/', 1)
        s3.download_file(bucket_name, key, local_path)
    except Exception as e:
        logging.error(f"Error downloading S3 object: {e}")

def upload_local_file_to_s3(s3, local_file: Path, object_name: str):
    """
    Upload a file from local to an S3 bucket
    i.e a csv or json metadata file.
    """
    if not local_file.exists():
        raise ValueError(f"{local_file} does not exist")
    bucket_name, key = object_name.split('/', 1)
    s3.upload_file(str(local_file), bucket_name, key)

def upload_local_files_to_s3(s3, local_files: List[Path], object_name: str):
    """
    Upload many something we have locally to a place on s3

    i.e a csv or json metadara file.
    """
    for local_file in local_files:
        upload_local_file_to_s3(s3, local_file, object_name)