import json
import os
from pathlib import Path
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws

from dpytools.s3.basic import (
    download_s3_file_content_to_local,
    get_s3_object,
    list_keys_in_path,
    move_s3_object,
    read_s3_file_content,
    read_s3_file_content_as_dict,
    s3_folder_recieved,
    upload_local_file_to_s3,
)

# Convenience reference path to the test_cases directory
this_case_dir = Path(Path(__file__).parent.parent / "test_cases")

TEST_REGION = "eu-west-2"
TEST_BUCKET_NAME = "test-bucket"

TEST_OBJECT_KEY = "test/object/key.txt"
TEST_OBJECT_VALUE = "testvalue"
TEST_OBJECT_FULL_PATH = f"{TEST_BUCKET_NAME}/{TEST_OBJECT_KEY}"

TEST_JSON_OBJECT_KEY = "test/object/json/key.json"
TEST_JSON_OBJECT_VALUE = {"key": "value"}
TEST_JSON_OBJECT_VALUE_BYTES = str.encode(json.dumps(TEST_JSON_OBJECT_VALUE))
TEST_JSON_OBJECT_FULL_PATH = f"{TEST_BUCKET_NAME}/{TEST_JSON_OBJECT_KEY}"


@pytest.fixture(scope="function")
def mock_s3(monkeypatch):
    """
    Return a mocked S3 client
    """
    with patch.dict(os.environ, clear=True):
        envvars = {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": TEST_REGION,
        }

        current_values = dict(os.environ)
        for key in current_values.keys():
            if "AWS_ENDPOINT" in key:
                envvars[key] = ""

        for k, v in envvars.items():
            monkeypatch.setenv(k, v)

        with mock_aws():
            yield boto3.client("s3")


@pytest.fixture()
def create_mock_objects(mock_s3):
    mock_s3.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": TEST_REGION},
    )
    mock_s3.put_object(
        Bucket=TEST_BUCKET_NAME, Body=TEST_OBJECT_VALUE, Key=TEST_OBJECT_KEY
    )
    mock_s3.put_object(
        Bucket=TEST_BUCKET_NAME,
        Body=TEST_JSON_OBJECT_VALUE_BYTES,
        Key=TEST_JSON_OBJECT_KEY,
    )
    return mock_s3


def test_get_s3_object(create_mock_objects):
    result = get_s3_object(TEST_OBJECT_FULL_PATH)
    assert result["Body"].read().decode() == TEST_OBJECT_VALUE


def test_read_s3_file_content(create_mock_objects):
    result = read_s3_file_content(TEST_OBJECT_FULL_PATH)
    assert result.decode() == TEST_OBJECT_VALUE


def test_read_s3_file_content_as_dict(create_mock_objects):
    result = read_s3_file_content_as_dict(TEST_JSON_OBJECT_FULL_PATH)

    assert result == TEST_JSON_OBJECT_VALUE


def test_read_s3_file_content_as_dict_raises_without_json_extension(
    create_mock_objects,
):
    """
    Attempting to use read_s3_file_content_as_dict against a non json
    file extension should raise a value error.
    """
    with pytest.raises(ValueError) as e:
        read_s3_file_content_as_dict(TEST_OBJECT_FULL_PATH)

    assert "Object name must end with '.json'" in str(e.value)


def test_download_s3_object_to_local(create_mock_objects, tmp_path):
    local_path = Path(f"{tmp_path}/output_file.txt")

    download_s3_file_content_to_local(TEST_OBJECT_FULL_PATH, str(local_path))

    assert local_path.read_text() == TEST_OBJECT_VALUE


def test_upload_local_file_to_s3_with_path(create_mock_objects, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of a Path.
    """
    local_file = tmp_path / "myfile"
    local_file.write_text(TEST_OBJECT_VALUE)

    upload_local_file_to_s3(local_file, TEST_OBJECT_FULL_PATH)

    client = boto3.client("s3")

    result = client.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY)

    assert result["Body"].read().decode() == TEST_OBJECT_VALUE


def test_upload_local_file_to_s3_with_str_as_path(create_mock_objects, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of str representing a Path.
    """
    local_file = tmp_path / "myfile"
    local_file.write_text(TEST_OBJECT_VALUE)

    upload_local_file_to_s3(str(local_file), TEST_OBJECT_FULL_PATH)

    client = boto3.client("s3")
    result = client.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY)

    assert result["Body"].read().decode() == TEST_OBJECT_VALUE


def test_upload_local_file_to_s3_raise_for_file_doesnt_exist(create_mock_objects):
    """
    Confirm we get the expected assertion error if the file to be
    uploaded does not exist
    """
    with pytest.raises(AssertionError) as e:
        upload_local_file_to_s3("im-not-a-file-that-exists", TEST_OBJECT_FULL_PATH)

    assert "does not exist." in str(e.value)


def test_s3_folder_recieved_downloads_files(create_mock_objects, tmp_path, monkeypatch):
    """
    Test that s3_folder_recieved downloads only files (ignoring keys that end with '/')
    from a specified folder in S3.
    """
    # Upload two file objects and one folder marker.
    create_mock_objects.put_object(
        Bucket=TEST_BUCKET_NAME, Body=b"file1 content", Key="folder/file1.txt"
    )
    create_mock_objects.put_object(
        Bucket=TEST_BUCKET_NAME, Body=b"file2 content", Key="folder/file2.txt"
    )

    # Folder marker; this key should be ignored.
    create_mock_objects.put_object(Bucket=TEST_BUCKET_NAME, Body=b"", Key="folder/")

    # Create an output directory (s3_folder_recieved will create it if needed).
    output_dir = tmp_path / "output"
    s3_folder_recieved(f"{TEST_BUCKET_NAME}/folder", output_dir)

    # Assert that the output directory was created.
    assert output_dir.exists()

    files_in_folder = os.listdir(output_dir)

    assert len(files_in_folder) == 2
    assert "file1.txt" in files_in_folder
    assert "file2.txt" in files_in_folder

    assert "folder/" not in files_in_folder


def test_move_s3_object_success(create_mock_objects):
    object_key = "file1.txt"
    object_content = "test content"
    create_mock_objects.put_object(
        Bucket=TEST_BUCKET_NAME, Body=str.encode(object_content), Key=object_key
    )

    target_key = "new/file/path.txt"
    move_s3_object(TEST_BUCKET_NAME, object_key, target_key)

    # Assert file copied
    matching_object = create_mock_objects.get_object(
        Bucket=TEST_BUCKET_NAME, Key=target_key
    )
    assert matching_object is not None
    matching_object["Body"].read().decode() == object_content

    # Assert file deleted
    with pytest.raises(Exception) as e:
        create_mock_objects.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert "The specified key does not exist" in str(e)


def test_move_s3_object_fails_when_missing_object(create_mock_objects):
    object_key = "file1.txt"
    target_key = "new/file/path.txt"

    with pytest.raises(Exception) as e:
        move_s3_object(TEST_BUCKET_NAME, object_key, target_key)
    assert "The specified key does not exist" in str(e)


def test_list_keys_in_path_finds_files(create_mock_objects):
    keys = list_keys_in_path(TEST_BUCKET_NAME, "test/object")
    assert len(keys) == 2

    assert TEST_OBJECT_KEY in keys
    assert TEST_JSON_OBJECT_KEY in keys


def test_list_keys_in_path_finds_no_files(create_mock_objects):
    keys = list_keys_in_path(TEST_BUCKET_NAME, "no/files/here")
    assert len(keys) == 0
