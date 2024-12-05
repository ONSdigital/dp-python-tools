import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from dpytools.http.token_auth import TokenAuth


def test_set_user_tokens():
    """
    Ensures that set_user_tokens() correctly sets the auth_token and id_token when the post request is successful.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {
        "Refresh": "test_refresh_token",
        "Authorization": "Bearer test_auth_token",
        "ID": "test_id_token",
    }
    with patch.object(TokenAuth, "post", return_value=mock_response):
        token_auth = TokenAuth()
        token_auth.set_user_tokens()
        assert token_auth.auth_token == "test_auth_token"
        assert token_auth.id_token == "test_id_token"


def test_set_user_tokens_failure():
    """
    Ensures that set_user_tokens() raises an exception when the post request is unsuccessful.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_response = MagicMock()
    mock_response.status_code = 400
    with patch.object(TokenAuth, "post", return_value=mock_response):
        with pytest.raises(Exception) as e_info:
            token_auth = TokenAuth()
            token_auth.set_user_tokens()
        assert str(e_info.value) == "Failed to create user tokens"


def test_get_auth_header_with_service_token():
    """
    Ensures that get_auth_header() returns the correct header when the service_token is set.
    """
    os.environ["SERVICE_TOKEN_FOR_UPLOAD"] = "test_token"
    token_auth = TokenAuth()
    header = token_auth.get_auth_header()
    assert header == {"Authorization": "Bearer test_token"}


def test_get_auth_header_with_user_token():
    """
    Ensures that get_auth_header() returns the correct header when the service_token is not set and the auth_token is less than 10 minutes old.
    """
    os.environ.pop("SERVICE_TOKEN_FOR_UPLOAD", None)
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {
        "Refresh": "test_refresh_token",
        "Authorization": "Bearer test_auth_token",
        "ID": "test_id_token",
    }
    with patch.object(TokenAuth, "post", return_value=mock_response):
        token_auth = TokenAuth()
        token_auth.set_user_tokens()
        header = token_auth.get_auth_header()
        assert header == {"X-Florence-Token": "test_auth_token", "ID": "test_id_token"}


def test_refresh_user_token():
    """
    Ensures that refresh_user_token() correctly updates the auth_token and id_token when the put request is successful.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.headers = {
        "Authorization": "Bearer new_auth_token",
        "ID": "new_id_token",
        "Refresh": "test_refresh_token",
    }
    with patch.object(
        TokenAuth, "put", return_value=mock_response
    ) as mock_put, patch.object(TokenAuth, "post", return_value=mock_response):
        token_auth = TokenAuth()
        token_auth.refresh_user_token()
        assert token_auth.auth_token.split()[1] == "new_auth_token"
        assert token_auth.id_token == "new_id_token"
        assert mock_put.call_count == 1


def test_refresh_user_token_failure():
    """
    Ensures that refresh_user_token() raises an exception when the put request is unsuccessful.
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_response = MagicMock()
    mock_response.status_code = 400
    with patch.object(TokenAuth, "put", return_value=mock_response), patch.object(
        TokenAuth, "post", return_value=mock_response
    ), patch.object(TokenAuth, "set_user_tokens"):
        token_auth = TokenAuth()
        # Manually set the necessary attributes
        token_auth.refresh_token = "test_refresh_token"
        token_auth.id_token = "test_id_token"
        token_auth.identity_api_url = os.environ["IDENTITY_API_URL"]
        # Mock token_creation_time to be more than 10 minutes in the past
        token_auth.token_creation_time = datetime.now() - timedelta(minutes=11)
        with pytest.raises(Exception) as e_info:
            token_auth.refresh_user_token()
        assert str(e_info.value) == "Refreshing token failed, returned a 400 error"
