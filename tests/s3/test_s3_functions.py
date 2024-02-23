import boto3
from moto import mock_aws
import pytest

from dpytools.s3.basic import (
    get_s3_object,
    read_s3_file_content,
    read_s3_file_content_as_dict,
    download_s3_file_content_to_local,
    upload_local_file_to_s3
)

@pytest.fixture
@mock_aws
def mock_s3_client():
    return boto3.client('s3')


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
