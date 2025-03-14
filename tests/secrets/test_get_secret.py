import base64
from datetime import datetime
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from dpytools.secrets.secret import _NO_SECRET_ERROR
from dpytools.secrets.secrets_client import _NO_RESPONSE_ERROR, SecretsClient


@patch("boto3.client")
def test_retrieves_secret_string(mock_secrets_manager_client):
    secret_value = "secret value here"
    secret_id = "secret id"

    mock_secrets_manager_client.return_value.get_secret_value.return_value = {
        "ARN": "string",
        "Name": secret_id,
        "SecretString": secret_value,
        "VersionStages": [
            "string",
        ],
        "CreatedDate": datetime(2015, 1, 1),
    }

    client = SecretsClient()

    secret = client.get_secret(secret_id)

    assert secret.success is True
    assert secret.value == secret_value
    assert secret.error is None
    assert secret.id == secret_id


@patch("boto3.client")
def test_retrieves_secret_binary(mock_secrets_manager_client):
    secret_value = b"secret value here"
    secret_id = "secret id"

    mock_secrets_manager_client.return_value.get_secret_value.return_value = {
        "ARN": "string",
        "Name": secret_id,
        "SecretBinary": base64.b64encode(secret_value),
        "VersionStages": [
            "string",
        ],
        "CreatedDate": datetime(2015, 1, 1),
    }

    client = SecretsClient()
    secret = client.get_secret(secret_id)

    assert secret.success is True
    assert secret.value == secret_value
    assert secret.error is None
    assert secret.id == secret_id


@patch("boto3.client")
def test_handles_no_secret_value(mock_secrets_manager_client):
    secret_id = "secret id"

    mock_secrets_manager_client.return_value.get_secret_value.return_value = {
        "ARN": "string",
        "Name": secret_id,
        "VersionStages": [
            "string",
        ],
    }

    client = SecretsClient()
    secret = client.get_secret("secret_id")

    assert secret.success is False
    assert secret.value is None
    assert _NO_SECRET_ERROR in secret.error
    assert secret.id == secret_id


@patch("boto3.client")
def test_handles_unknown_error(mock_secrets_manager_client):
    error_message = "Test error message"
    mock_secrets_manager_client.return_value.get_secret_value.side_effect = Exception(
        "Test error message"
    )

    client = SecretsClient()
    secret_id = "secret id to fetch"
    secret = client.get_secret(secret_id)

    assert secret.success is False
    assert secret.value is None
    assert error_message in secret.error
    assert "An unknown error occurred retrieving the secret" in secret.error
    assert secret.id == secret_id


@patch("boto3.client")
def test_handles_none_response(mock_secrets_manager_client):
    mock_secrets_manager_client.return_value.get_secret_value.return_value = None
    client = SecretsClient()

    secret_id = "secret_id"
    secret = client.get_secret(secret_id)

    assert secret.success is False
    assert secret.value is None
    assert _NO_RESPONSE_ERROR in secret.error
    assert secret.id == secret_id


exception_secret_id = "secret_id"
exception_data = [
    (
        "ResourceNotFoundException",
        f"The requested secret {exception_secret_id} was not found",
    ),
    ("InvalidRequestException", "The request was invalid due to: "),
    ("InvalidParameterException", "The request had invalid params:"),
    (
        "DecryptionFailure",
        "The requested secret can't be decrypted using the provided KMS key:",
    ),
    ("InternalServiceError", "An error occurred on service side: "),
    ("Not a handled error", "An unknown error occurred"),
]


@pytest.mark.parametrize("exception_code,expected_error", exception_data)
@patch("boto3.client")
def test_handles_client_exceptions(
    mock_secrets_manager_client, exception_code: str, expected_error: str
):
    error = {"Error": {"Code": exception_code}}
    mock_secrets_manager_client.return_value.get_secret_value.side_effect = ClientError(
        error_response=error, operation_name="get_secret_value"
    )

    client = SecretsClient()
    secret_id = "secret_id"
    secret = client.get_secret(secret_id)

    assert secret.success is False
    assert secret.value is None
    assert expected_error in secret.error
    assert secret.id == secret_id
