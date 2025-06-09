import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from requests import HTTPError
import pytest

from dpytools.http.upload.upload_service_client import UploadServiceClient


def mock_successful_token_response(*args, **kwargs):
    """
    Mocks a successful token response for the TokenAuth class.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {
        "Refresh": "test_refresh_token",
        "Authorization": "Bearer test_auth_token",
        "ID": "test_id_token",
    }
    return mock_response

def mock_successful_response_chunk_upload(*args, **kwargs):
    """
    Mocks a successful response for _upload_file_chunk.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201

    return mock_response


def mock_bad_response_chunk_upload(*args, **kwargs):
    """
    Mocks a bad response for _upload_file_chunk.
    """
    mock_response = MagicMock()
    mock_response.status_code = 400

    return mock_response


@patch("dpytools.http.upload.upload_service_client._create_temp_chunks")
@patch("dpytools.http.upload.upload_service_client._delete_temp_chunks")
@patch("dpytools.http.upload.upload_service_client._generate_upload_params")
@patch(
    "dpytools.http.upload.upload_service_client.UploadServiceClient._upload_file_chunks"
)
@patch("requests.request", side_effect=mock_successful_token_response)
def test_upload(
    mock_request,
    mock_upload_file_chunks,
    mock_generate_upload_params,
    mock_delete_temp_chunks,
    mock_create_temp_chunks,
):
    """
    Ensures that the _upload method works correctly.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = UploadServiceClient(upload_url="http://example.com/upload")
    mock_create_temp_chunks.return_value = ["chunk1", "chunk2"]
    mock_generate_upload_params.return_value = {"resumableIdentifier": "test_id"}

    client.upload(file_path="tests/test_cases/countries.csv", mimetype="text/csv")

    mock_create_temp_chunks.assert_called_once_with(
        Path("tests/test_cases/countries.csv").absolute(), 5242880
    )
    mock_generate_upload_params.assert_called_once_with(
        Path("tests/test_cases/countries.csv").absolute(), "text/csv", 5242880
    )
    mock_upload_file_chunks.assert_called_once_with(
        ["chunk1", "chunk2"], {"resumableIdentifier": "test_id"}
    )
    mock_delete_temp_chunks.assert_called_once_with(["chunk1", "chunk2"])


@patch("dpytools.http.upload.upload_service_client._create_temp_chunks")
@patch("dpytools.http.upload.upload_service_client._delete_temp_chunks")
@patch("dpytools.http.upload.upload_service_client._generate_upload_new_params")
@patch(
    "dpytools.http.upload.upload_service_client.UploadServiceClient._upload_file_chunks"
)
@patch("requests.request", side_effect=mock_successful_token_response)
def test_upload_new(
    mock_request,
    mock_upload_file_chunks,
    mock_generate_upload_new_params,
    mock_delete_temp_chunks,
    mock_create_temp_chunks,
):
    """
    Ensures that the _upload_new method works correctly.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = UploadServiceClient(upload_url="http://example.com/upload")
    mock_create_temp_chunks.return_value = ["chunk1", "chunk2"]
    mock_generate_upload_new_params.return_value = {"Path": "test_path"}

    client.upload_new(
        file_path="tests/test_cases/countries.csv",
        mimetype="text/csv",
        chunk_size=5242880,
        alias_name="test_alias",
        title="test_title",
        is_publishable=True,
        licence="test_licence",
        licence_url="http://test_licence_url",
        collection_id="test_collection_id",
    )

    mock_create_temp_chunks.assert_called_once_with(
        Path("tests/test_cases/countries.csv").absolute(), 5242880
    )
    mock_generate_upload_new_params.assert_called_once_with(
        Path("tests/test_cases/countries.csv").absolute(),
        "text/csv",
        5242880,
        "test_alias",
        "test_title",
        True,
        "test_licence",
        "http://test_licence_url",
        "test_collection_id",
    )
    mock_upload_file_chunks.assert_called_once_with(
        ["chunk1", "chunk2"], {"Path": "test_path"}
    )
    mock_delete_temp_chunks.assert_called_once_with(["chunk1", "chunk2"])


@patch("dpytools.http.upload.upload_service_client._create_temp_chunks")
@patch("dpytools.http.upload.upload_service_client._generate_upload_new_params")
@patch(
    "requests.request", side_effect=[
        mock_successful_token_response, 
        mock_successful_response_chunk_upload, 
        mock_successful_response_chunk_upload, 
        mock_bad_response_chunk_upload
        ]
)
def test_upload_file_chunks(
    mock_request,
    mock_generate_upload_new_params,
    mock_create_temp_chunks,
):
    """
    Ensures that the _upload_file_chunks captures error correctly.
    """

    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"

    client = UploadServiceClient(upload_url="http://example.com/upload")
    mock_create_temp_chunks.return_value = ["chunk1", "chunk2"]
    mock_generate_upload_new_params.return_value = {"Path": "test_path"}

    # expecting a succesful upload from first call of _upload_file_chunks
    response = client._upload_file_chunks(
        mock_create_temp_chunks,
        mock_generate_upload_new_params
    )

    assert response.status_code == 201
    
    # expecting a failed upload from second call of _upload_file_chunks
    with pytest.raises(HTTPError):
        client._upload_file_chunks(
            mock_create_temp_chunks,
            mock_generate_upload_new_params
        )
