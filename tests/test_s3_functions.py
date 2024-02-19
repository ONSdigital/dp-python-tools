import boto3
from moto import mock_s3
from pathlib import Path
from basic import setup_session, get_s3_object, get_s3_object_as_dict, download_s3_object_to_local, upload_local_file_to_s3, upload_local_files_to_s3

@mock_s3
def test_setup_session():
    s3 = setup_session('test-profile')
    assert isinstance(s3, boto3.resources.base.ServiceResource)

@mock_s3
def test_get_s3_object():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='mybucket')
    conn.Object('mybucket', 'mykey').put(Body='myvalue')

    s3 = setup_session('test-profile')
    result = get_s3_object(s3, 'mybucket/mykey')
    assert result == b'myvalue'

@mock_s3
def test_get_s3_object_as_dict():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='mybucket')
    conn.Object('mybucket', 'mykey.json').put(Body='{"key": "value"}')

    s3 = setup_session('test-profile')
    result = get_s3_object_as_dict(s3, 'mybucket/mykey.json')
    assert result == {"key": "value"}

@mock_s3
def test_download_s3_object_to_local(tmp_path):
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='mybucket')
    conn.Object('mybucket', 'mykey').put(Body='myvalue')

    s3 = setup_session('test-profile')
    local_path = tmp_path / 'mykey'
    download_s3_object_to_local(s3, 'mybucket/mykey', str(local_path))

    assert local_path.read_text() == 'myvalue'

@mock_s3
def test_upload_local_file_to_s3(tmp_path):
    local_file = tmp_path / 'myfile'
    local_file.write_text('myvalue')

    s3 = setup_session('test-profile')
    upload_local_file_to_s3(s3, local_file, 'mybucket/mykey')

    conn = boto3.resource('s3', region_name='us-east-1')
    result = conn.Object('mybucket', 'mykey').get()['Body'].read().decode()

    assert result == 'myvalue'

@mock_s3
def test_upload_local_files_to_s3(tmp_path):
    local_file1 = tmp_path / 'myfile1'
    local_file1.write_text('myvalue1')
    local_file2 = tmp_path / 'myfile2'
    local_file2.write_text('myvalue2')

    s3 = setup_session('test-profile')
    upload_local_files_to_s3(s3, [local_file1, local_file2], 'mybucket/mykey')

    conn = boto3.resource('s3', region_name='us-east-1')
    result1 = conn.Object('mybucket', 'mykey/myfile1').get()['Body'].read().decode()
    result2 = conn.Object('mybucket', 'mykey/myfile2').get()['Body'].read().decode()

    assert result1 == 'myvalue1'
    assert result2 == 'myvalue2'