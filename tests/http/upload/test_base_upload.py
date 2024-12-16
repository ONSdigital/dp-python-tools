import os
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
        "Authorization": "Bearer test_auth_token",
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
    assert client.token_auth.auth_token == "test_auth_token"
    assert client.token_auth.id_token == "test_id_token"
