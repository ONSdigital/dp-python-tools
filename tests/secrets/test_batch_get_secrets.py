import json
from typing import List, Optional
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from dpytools.secrets.secrets_client import _NO_RESPONSE_ERROR, SecretsClient
from tests.secrets.helpers import create_error, create_random_string, create_secret

success_secret_ids = ["secret_one", "json_test", "json_with_matching_key_test"]
success_secret_values = [
    "this is the first secret's value",
    '{"test_key": "test value"}',
    "this should be the result",
]
secrets = {
    success_secret_ids[0]: create_secret(
        name=success_secret_ids[0], secret_string=success_secret_values[0]
    ),
    success_secret_ids[1]: create_secret(
        name=success_secret_ids[1], secret_string=success_secret_values[1]
    ),
    success_secret_ids[2]: create_secret(
        name=success_secret_ids[2],
        secret_string=f'{{"{success_secret_ids[2]}": "{success_secret_values[2]}"}}',
    ),
}

errored_secret_ids = [
    "errored_secret_one",
    "errored_secret_two",
    "also_an_errored_secret",
]
errors = {
    errored_secret_ids[0]: create_error(
        secret_id=errored_secret_ids[0], message="Error message", error_code="1234"
    ),
    errored_secret_ids[1]: create_error(
        secret_id=errored_secret_ids[1],
        message="Second error message",
        error_code="ABCD",
    ),
    errored_secret_ids[2]: create_error(
        secret_id=errored_secret_ids[2],
        message="The final error message",
        error_code="1234",
    ),
}

combined_secret_ids = [*success_secret_ids, *errored_secret_ids]


def create_response(
    secrets: Optional[List[dict]] = None, errors: Optional[List[dict]] = None
) -> dict:
    # From testing, the SecretValues + Errors keys seem to return with an empty array, not null/not supplied, if none matching
    return {
        "SecretValues": secrets if secrets is not None else [],
        "Errors": errors if errors is not None else [],
        # Not using NextToken anywhere currently but in the response.
        # Not sure if 12 is correct length, but since there's no implementation/usage of it on our end shouldn't matter
        "NextToken": create_random_string(length=12),
    }


def batch_get_secrets_mock(SecretIdList=List[str]) -> dict:
    successful_secrets = []
    errored = []

    for id in SecretIdList:
        if id in secrets:
            successful_secrets.append(secrets[id])
        elif id in errored_secret_ids:
            errored.append(errors[id])

    response = create_response(secrets=successful_secrets, errors=errored)
    return response


def validate_success_secrets(batch_response):
    for index, secret_id in enumerate(success_secret_ids):
        returned = batch_response.secrets[secret_id]
        assert returned.error is None
        assert returned.success

        expected_value = success_secret_values[index]
        if isinstance(returned.value, dict):
            expected_value = json.loads(expected_value)

        assert returned.value == expected_value


def validate_errors(batch_response):
    for index, secret_id in enumerate(errored_secret_ids):
        returned = batch_response.secrets[secret_id]
        assert returned.error is not None
        assert not returned.success

        matching_error = errors[secret_id]
        assert returned.error == matching_error["Message"]


@patch("boto3.client")
def test_retrieves_secrets_successfully(mock_secrets_manager_client):
    mock_secrets_manager_client.return_value.batch_get_secret_value.side_effect = (
        batch_get_secrets_mock
    )
    client = SecretsClient()

    batch_response = client.batch_get_secrets(success_secret_ids)

    assert batch_response.success is True
    assert batch_response.error is None
    assert len(batch_response.secrets) == len(success_secret_ids)

    validate_success_secrets(batch_response)


@patch("boto3.client")
def test_retrieves_parses_errors(mock_secrets_manager_client):
    mock_secrets_manager_client.return_value.batch_get_secret_value.side_effect = (
        batch_get_secrets_mock
    )
    client = SecretsClient()

    batch_response = client.batch_get_secrets(combined_secret_ids)

    assert batch_response.success is True
    assert batch_response.error is None
    assert len(batch_response.secrets) == len(combined_secret_ids)

    validate_success_secrets(batch_response)
    validate_errors(batch_response)


@patch("boto3.client")
def test_handles_missing_secret_ids(mock_secrets_manager_client):
    mock_secrets_manager_client.return_value.batch_get_secret_value.side_effect = (
        batch_get_secrets_mock
    )
    client = SecretsClient()

    missing_secret_ids = ["missing_id_one", "other_missing_id"]
    secret_ids = [*combined_secret_ids, *missing_secret_ids]
    batch_response = client.batch_get_secrets(secret_ids)

    assert batch_response.success is True
    assert batch_response.error is None
    assert len(batch_response.secrets) == len(secret_ids)

    validate_success_secrets(batch_response)
    validate_errors(batch_response)

    for missing_id in missing_secret_ids:
        matching = batch_response.secrets[missing_id]

        assert matching is not None
        assert not matching.success
        assert matching.value is None
        assert matching.error == f"Secret ID {missing_id} not returned in response"


exception_data = [
    (
        "ResourceNotFoundException",
        f"The requested secret {', '.join(combined_secret_ids)} was not found",
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
def test_handles_managed_exceptions(
    mock_secrets_manager_client, exception_code: str, expected_error: str
):
    error = {"Error": {"Code": exception_code}}
    mock_secrets_manager_client.return_value.batch_get_secret_value.side_effect = (
        ClientError(error_response=error, operation_name="batch_get_secret_value")
    )
    client = SecretsClient()

    response = client.batch_get_secrets(combined_secret_ids)

    assert not response.success
    assert expected_error in response.error
    assert response.secrets is None


@patch("boto3.client")
def test_handles_doesnt_handle_nonclienterror_exceptions(mock_secrets_manager_client):
    error_message = "This exception is not handled"
    mock_secrets_manager_client.return_value.batch_get_secret_value.side_effect = (
        Exception(error_message)
    )
    client = SecretsClient()
    with pytest.raises(Exception) as e:
        response = client.batch_get_secrets(combined_secret_ids)
        assert response is None
        assert str(e) == error_message


@patch("boto3.client")
def test_handles_empty_response(mock_secrets_manager_client):
    mock_secrets_manager_client.return_value.batch_get_secret_value.return_value = None
    client = SecretsClient()

    response = client.batch_get_secrets(combined_secret_ids)

    assert not response.success
    assert response.secrets is None
    assert response.error == _NO_RESPONSE_ERROR
