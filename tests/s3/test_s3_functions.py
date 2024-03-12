import boto3
from moto import mock_aws
import pytest
from pathlib import Path
import tarfile
import tempfile

from dpytools.s3.basic import (
    get_s3_object,
    read_s3_file_content,
    read_s3_file_content_as_dict,
    download_s3_file_content_to_local,
    upload_local_file_to_s3,
    decompress_s3_tar
)

# Convenience reference path to the test_cases directory
this_case_dir = Path(Path(__file__).parent.parent / "test_cases")

@pytest.fixture
@mock_aws
def mock_s3_client():
    return boto3.client('s3')

@pytest.fixture
def path_to_mostly_empty_csv():
    return Path(this_case_dir / "decompress_from_s3.csv").absolute()

@pytest.fixture
def path_to_mostly_empty_json():
    return Path(this_case_dir / "decompress_from_s3.json").absolute()


@mock_aws
def test_get_s3_object(mock_s3_client):
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    mock_s3_client.put_object(
        Bucket='mybucket',
        Body="myvalue",
        Key="mykey"
    )
    
    result = get_s3_object('mybucket/mykey')
    assert result['Body'].read() == b'myvalue'


@mock_aws
def test_read_s3_file_content(mock_s3_client):
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    mock_s3_client.put_object(
        Bucket='mybucket',
        Body="myvalue",
        Key="mykey"
    )
    result = read_s3_file_content('mybucket/mykey')
    assert result == b"myvalue"


@mock_aws
def test_read_s3_file_content_as_dict(mock_s3_client):
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    mock_s3_client.put_object(
        Bucket='mybucket',
        Body=b'{"key":"value"}',
        Key="mykey.json"
    )
    result = read_s3_file_content_as_dict('mybucket/mykey.json')
    assert result == {"key":"value"}


@mock_aws
def test_read_s3_file_content_as_dict_raises_without_json_extension():
    """
    Attempting to use read_s3_file_content_as_dict against a non json
    file extension should raise a value error.
    """
    with pytest.raises(ValueError) as e:
        read_s3_file_content_as_dict('mybucket/mykey')

    assert "Object name must end with '.json'" in str(e.value)


@mock_aws
def test_download_s3_object_to_local(mock_s3_client, tmp_path):
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    mock_s3_client.put_object(
        Bucket='mybucket',
        Body=b'myvalue',
        Key="mykey"
    )
    local_path = tmp_path / 'mykey'

    download_s3_file_content_to_local('mybucket/mykey', str(local_path))

    assert local_path.read_text() == 'myvalue'


@mock_aws
def test_upload_local_file_to_s3_with_path(mock_s3_client, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of a Path. 
    """
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    local_file = tmp_path / 'myfile'
    local_file.write_text('myvalue')

    upload_local_file_to_s3(local_file, 'mybucket/mykey')

    result = mock_s3_client.get_object(Bucket='mybucket', Key='mykey')

    assert result["Body"].read() == b'myvalue'


@mock_aws
def test_upload_local_file_to_s3_with_str_as_path(mock_s3_client, tmp_path):
    """
    Confirm user can upload a file given a file location in the form
    of str representing a Path. 
    """
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    local_file = tmp_path / 'myfile'
    local_file.write_text('myvalue')

    upload_local_file_to_s3(str(local_file), 'mybucket/mykey')

    result = mock_s3_client.get_object(Bucket='mybucket', Key='mykey')

    assert result["Body"].read() == b'myvalue'


@mock_aws
def test_upload_local_file_to_s3_raise_for_file_doesnt_exist(mock_s3_client):
    """
    Confirm we get the expected assertion error if the file to be
    uploaded does not exist
    """
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })

    with pytest.raises(AssertionError) as e:
        upload_local_file_to_s3("im-not-a-file-that-exists", 'mybucket/mykey')

    assert "does not exist." in str(e.value)

@mock_aws
def test_decompress_s3_tar_with_given_dir_path(mock_s3_client, tmp_path, path_to_mostly_empty_csv, path_to_mostly_empty_json):
    """
    By creating a s3 bucket and uploding a tar file to it, 
    confirm that the user can get the tar file from the s3 bucket and
    decompress it to a given directory.
    """

    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-1"
    })
    tar_file = tmp_path / 's3.tar'

    with tarfile.open(tar_file, 'a') as tar:
      tar.add(path_to_mostly_empty_csv, arcname=path_to_mostly_empty_csv.name)
      tar.add(path_to_mostly_empty_json, arcname=path_to_mostly_empty_json.name)

    upload_local_file_to_s3(tar_file, 'mybucket/s3.tar')

    # Just download to a child directory of our existing tmp path to enable
    # automatic test cleanup
    output_dir = Path(tmp_path / "output")
    decompress_s3_tar('mybucket/s3.tar', output_dir)

    assert Path(output_dir).exists()
    assert Path(output_dir / path_to_mostly_empty_json.name).exists()
    assert Path(output_dir / path_to_mostly_empty_csv.name).exists() 


@mock_aws
def test_decompress_s3_tar_raises_error_when_file_is_not_tar(mock_s3_client):
    """
    Confirm we get the expected assertion error if the file to be
    uploaded does not exist
    """
    mock_s3_client.create_bucket(Bucket='mybucket', CreateBucketConfiguration={
        'LocationConstraint': "eu-west-2"
    })
    local_file = 'tests/test_cases/decompress_from_s3.json'

    upload_local_file_to_s3(local_file, 'mybucket/mykey')

    with pytest.raises(NotImplementedError) as e:
        decompress_s3_tar('mybucket/mykey', "outputs")

    assert "This function currently only handles archives using the tar extension" in str(e.value)

