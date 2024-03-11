import os
from pathlib import Path

import pytest
from dpytools.http.upload import UploadClient


@pytest.mark.vcr(record_mode="once")
def test_upload():
    """
    Ensures that the upload() method successfully chunks the given csv file and uploads it to the correct S3 bucket (HTTP request and response recorded in http/cassettes/test_upload_new.yaml)
    """
    upload_client = UploadClient(upload_url="http://localhost:11850/upload")
    s3_key, s3_url = upload_client.upload(
        csv_path="tests/test_cases/countries.csv",
        s3_path="https://s3-eu-west-2.amazonaws.com/ons-dp-sandbox-publishing-uploaded-datasets",
    )
    assert (
        s3_url
        == "https://s3-eu-west-2.amazonaws.com/ons-dp-sandbox-publishing-uploaded-datasets/"
        + s3_key
    )


def test_create_and_delete_temp_chunks():
    """
    Ensures that the _create_temp_chunks() method creates the correct number of file chunks and that the _delete_temp_chunks() method deletes the temporary files.
    """
    upload_client = UploadClient(upload_url="http://example.org/upload")
    temp_file_paths_list = upload_client._create_temp_chunks(
        csv_path="tests/test_cases/countries.csv"
    )
    assert len(temp_file_paths_list) == 2
    assert "temp-file-part-1" in temp_file_paths_list[0]
    upload_client._delete_temp_chunks(temp_file_paths_list)
    assert os.path.exists(Path(temp_file_paths_list[0]).absolute()) == False
