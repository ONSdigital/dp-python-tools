
import boto3
import tarfile
import requests
from io import BytesIO
from pathlib import Path
from typing import Optional


# def decompress_s3_tar(s3_url: str, directory: Optional[Path]):
#     """
#     Given a url to an s3 object that is a tar file, decompress it
#     to the provided directory path.
#     """
#     # Make sure it actually is a tar file.
#     # Decompress all the files to the directory specified.
#     # If the directory does not exist, create it
#     # If it does exist, raise an error
#     # If no path  is provided assume the current working directory
#     ...

#     s3 = boto3.client('s3')
#     obj = s3.get_object(Bucket="decompress-from-s3", Key="s3_bucket.tar")
#     print("hello")

def decompress_s3_tar(s3_url: str, directory: Optional[Path]):
    r = requests.get(s3_url)
    print(r.status_code)
    print(r.headers['content-type'])
    print(r.text)

    tar = tarfile.open(fileobj=BytesIO(r.content),mode='r:*')
    tar.extractall(path=directory)
    tar.close()


s3_object_url = "https://decompress-from-s3.s3.eu-west-2.amazonaws.com/s3_bucket.tar"
decompress_s3_tar(s3_object_url, "outputs")
