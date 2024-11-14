import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from dpytools.http.upload.base_upload import BaseUploadClient


def mock_successful_token_response(*args, **kwargs):
    """
    Mocks a successful token response for the TokenAuth class.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {
        "Refresh": "test_refresh_token",
        "Authorization": "test_auth_token",
        "ID": "test_id_token",
    }
    return mock_response


@patch("requests.request", side_effect=mock_successful_token_response)
def test_base_upload_client_init(mock_request):
    """
    Ensures that the BaseUploadClient initializes correctly with the given parameters.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = BaseUploadClient(upload_url="http://example.com/upload", backoff_max=30)
    assert client.upload_url == "http://example.com/upload"
    assert client.token_auth.backoff_max == 30


@patch("dpytools.http.upload.base_upload._create_temp_chunks")
@patch("dpytools.http.upload.base_upload._delete_temp_chunks")
@patch("dpytools.http.upload.base_upload._generate_upload_params")
@patch("dpytools.http.upload.base_upload.BaseUploadClient._upload_file_chunks")
@patch("requests.request", side_effect=mock_successful_token_response)
def test_upload(mock_request, mock_upload_file_chunks, mock_generate_upload_params, mock_delete_temp_chunks, mock_create_temp_chunks):
    """
    Ensures that the _upload method works correctly.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = BaseUploadClient(upload_url="http://example.com/upload", backoff_max=30)
    mock_create_temp_chunks.return_value = ["chunk1", "chunk2"]
    mock_generate_upload_params.return_value = {"resumableIdentifier": "test_id"}

    client._upload(file_path="test_file.csv", mimetype="text/csv")

    mock_create_temp_chunks.assert_called_once_with(Path("test_file.csv").absolute(), 5242880)
    mock_generate_upload_params.assert_called_once_with(Path("test_file.csv").absolute(), "text/csv", 5242880)
    mock_upload_file_chunks.assert_called_once_with(["chunk1", "chunk2"], {"resumableIdentifier": "test_id"})
    mock_delete_temp_chunks.assert_called_once_with(["chunk1", "chunk2"])


@patch("dpytools.http.upload.base_upload._create_temp_chunks")
@patch("dpytools.http.upload.base_upload._delete_temp_chunks")
@patch("dpytools.http.upload.base_upload._generate_upload_new_params")
@patch("dpytools.http.upload.base_upload.BaseUploadClient._upload_file_chunks")
@patch("requests.request", side_effect=mock_successful_token_response)
def test_upload_new(mock_request, mock_upload_file_chunks, mock_generate_upload_new_params, mock_delete_temp_chunks, mock_create_temp_chunks):
    """
    Ensures that the _upload_new method works correctly.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = BaseUploadClient(upload_url="http://example.com/upload", backoff_max=30)
    mock_create_temp_chunks.return_value = ["chunk1", "chunk2"]
    mock_generate_upload_new_params.return_value = {"Path": "test_path"}

    client._upload_new(
        file_path="test_file.csv",
        mimetype="text/csv",
        chunk_size=5242880,
        alias_name="test_alias",
        title="test_title",
        is_publishable=True,
        license="test_license",
        license_url="http://test_license_url"
    )

    mock_create_temp_chunks.assert_called_once_with(Path("test_file.csv").absolute(), 5242880)
    mock_generate_upload_new_params.assert_called_once_with(
        Path("test_file.csv").absolute(),
        "text/csv",
        5242880,
        "test_alias",
        "test_title",
        True,
        "test_license",
        "http://test_license_url"
    )
    mock_upload_file_chunks.assert_called_once_with(["chunk1", "chunk2"], {"Path": "test_path"})
    mock_delete_temp_chunks.assert_called_once_with(["chunk1", "chunk2"])

