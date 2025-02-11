import tarfile
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from dpytools.s3.basic import (
    download_s3_file_content_to_local,
    get_s3_object,
    read_s3_file_content,
    read_s3_file_content_as_dict,
    s3_folder_recieved,
    upload_local_file_to_s3,
)

# Convenience reference path to the test_cases directory
this_case_dir = Path(Path(__file__).parent.parent / "test_cases")


@pytest.fixture
@mock_aws
def mock_s3_client():
    return boto3.client("s3")


@pytest.fixture
def path_to_mostly_empty_csv():
    return Path(this_case_dir / "decompress_from_s3.csv").absolute()


@pytest.fixture
def path_to_mostly_empty_json():
    return Path(this_case_dir / "decompress_from_s3.json").absolute()


@mock_aws
def test_get_s3_object(mock_s3_client):
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    mock_s3_client.put_object(Bucket="mybucket", Body="myvalue", Key="mykey")

    result = get_s3_object("mybucket/mykey")
    assert result["Body"].read() == b"myvalue"


@mock_aws
def test_read_s3_file_content(mock_s3_client):
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    mock_s3_client.put_object(Bucket="mybucket", Body="myvalue", Key="mykey")
    result = read_s3_file_content("mybucket/mykey")
    assert result == b"myvalue"


@mock_aws
def test_read_s3_file_content_as_dict(mock_s3_client):
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    mock_s3_client.put_object(
        Bucket="mybucket", Body=b'{"key":"value"}', Key="mykey.json"
    )
    result = read_s3_file_content_as_dict("mybucket/mykey.json")
    assert result == {"key": "value"}


@mock_aws
def test_read_s3_file_content_as_dict_raises_without_json_extension():
    """
    Attempting to use read_s3_file_content_as_dict against a non json
    file extension should raise a value error.
    """
    with pytest.raises(ValueError) as e:
        read_s3_file_content_as_dict("mybucket/mykey")

    assert "Object name must end with '.json'" in str(e.value)


@mock_aws
def test_download_s3_object_to_local(mock_s3_client, tmp_path):
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    mock_s3_client.put_object(Bucket="mybucket", Body=b"myvalue", Key="mykey")
    local_path = tmp_path / "mykey"

    download_s3_file_content_to_local("mybucket/mykey", str(local_path))

    assert local_path.read_text() == "myvalue"


@mock_aws
def test_upload_local_file_to_s3_with_path(mock_s3_client, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of a Path.
    """
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    local_file = tmp_path / "myfile"
    local_file.write_text("myvalue")

    upload_local_file_to_s3(local_file, "mybucket/mykey")

    result = mock_s3_client.get_object(Bucket="mybucket", Key="mykey")

    assert result["Body"].read() == b"myvalue"


@mock_aws
def test_upload_local_file_to_s3_with_str_as_path(mock_s3_client, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of str representing a Path.
    """
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    local_file = tmp_path / "myfile"
    local_file.write_text("myvalue")

    upload_local_file_to_s3(str(local_file), "mybucket/mykey")

    result = mock_s3_client.get_object(Bucket="mybucket", Key="mykey")

    assert result["Body"].read() == b"myvalue"


@mock_aws
def test_upload_local_file_to_s3_raise_for_file_doesnt_exist(mock_s3_client):
    """
    Confirm we get the expected assertion error if the file to be
    uploaded does not exist
    """
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )

    with pytest.raises(AssertionError) as e:
        upload_local_file_to_s3("im-not-a-file-that-exists", "mybucket/mykey")

    assert "does not exist." in str(e.value)

@mock_aws
def test_s3_folder_recieved_downloads_files(mock_s3_client, tmp_path, monkeypatch):
    """
    Test that s3_folder_recieved downloads only files (ignoring keys that end with '/')
    from a specified folder in S3.
    """
    # Create the bucket.
    mock_s3_client.create_bucket(
        Bucket="mybucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )
    # Upload two file objects and one folder marker.
    mock_s3_client.put_object(Bucket="mybucket", Body=b"file1 content", Key="folder/file1.txt")
    mock_s3_client.put_object(Bucket="mybucket", Body=b"file2 content", Key="folder/file2.txt")
    # Folder marker; this key should be ignored.
    mock_s3_client.put_object(Bucket="mybucket", Body=b"", Key="folder/")

    # Ensure that _get_s3_client returns our mocked client.
    monkeypatch.setattr("dpytools.s3.basic._get_s3_client", lambda profile_name=None: mock_s3_client)

    # Prepare a list to capture the keys passed to download_fileobj.
    downloaded_keys = []
    original_download_fileobj = mock_s3_client.download_fileobj

    def fake_download_fileobj(Bucket, Key, Fileobj, ExtraArgs=None, Callback=None, Config=None):
        downloaded_keys.append(Key)
        return original_download_fileobj(Bucket, Key, Fileobj, ExtraArgs, Callback, Config)

    # Override the download_fileobj method on our mocked client.
    mock_s3_client.download_fileobj = fake_download_fileobj

    # Create an output directory (s3_folder_recieved will create it if needed).
    output_dir = tmp_path / "output"
    s3_folder_recieved("mybucket/folder", output_dir)

    # Assert that the output directory was created.
    assert output_dir.exists()

    # Verify that download_fileobj was called only for file objects.
    # Since we uploaded two files, we expect two calls.
    assert len(downloaded_keys) == 2
    assert "folder/file1.txt" in downloaded_keys
    assert "folder/file2.txt" in downloaded_keys
    # The folder marker key should not trigger a download.
    assert "folder/" not in downloaded_keys

