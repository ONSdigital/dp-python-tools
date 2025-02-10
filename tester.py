from dpytools.s3.basic import s3_folder_recieved

import os
import boto3


os.environ["AWS_PROFILE"] = "dp-sandbox"
boto3.setup_default_session()
bucket = "dp-sandbox-ingest-submission-bucket"
key = "test-upload-folder/"
client = boto3.client("s3")
list_objects = client.list_objects_v2(Bucket=bucket, Prefix=key)

object_name = "dp-sandbox-ingest-submission-bucket/test-upload-folder/"
bucket_name = object_name.split("/")[0]


s3_folder_recieved(object_name, "input")