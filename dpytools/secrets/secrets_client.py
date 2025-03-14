from typing import List

import boto3
from botocore.exceptions import ClientError

from dpytools.secrets.batch_get_secrets_result import BatchGetSecretsResult
from dpytools.secrets.secret import Secret

_CLIENT_NAME = "secretsmanager"

_NO_RESPONSE_ERROR = "Did not receive a response from AWS"


class SecretsClient:
    """
    Wrapper around AWS Secrets Manager.

    Initialises the client using boto3 and then retrieves secrets with handling of the responses.
    """

    def __init__(self):
        self.client = boto3.client(_CLIENT_NAME)

    def get_secret(self, secret_id: str) -> Secret:
        """
        Retrieves the given secret from AWS Secrets Manager.

        :param secret_id: The secret ID/name that we need to retrieve

        :return: An object containing the value of the secret if successful, otherwise an error message describing the problem.
        """
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)
        except ClientError as e:
            error = self._get_error_message(secret_id, e)
            return Secret(error=error, id=secret_id)
        except Exception as e:
            return Secret(
                error=f"An unknown error occurred retrieving the secret {secret_id} from AWS Secrets Manager: {e}",
                id=secret_id,
            )

        if get_secret_value_response is None:
            return Secret(error=_NO_RESPONSE_ERROR, id=secret_id)

        return Secret(response=get_secret_value_response, id=secret_id)

    def batch_get_secrets(self, secret_ids: List[str]) -> BatchGetSecretsResult:
        """
        Retrieve multiple secrets at once

        :param secret_ids: Secret IDs to retrieve

        :return: Parsed response
        """
        try:
            response = self.client.batch_get_secret_value(SecretIdList=secret_ids)

            if response is None:
                return BatchGetSecretsResult(
                    error=_NO_RESPONSE_ERROR, secret_ids=secret_ids
                )

            return BatchGetSecretsResult(aws_response=response, secret_ids=secret_ids)
        except ClientError as e:
            error = self._get_error_message(", ".join(secret_ids), e)
            return BatchGetSecretsResult(error=error, secret_ids=secret_ids)

    def _get_error_message(self, secret_id: str, e: ClientError) -> str:
        """
        Handle ClientError returned from SecretsManager client, and return a more
        descriptive error message.

        :param secret_id: The ID of the secret we were attempting to retrieve
        :param e: ClientError thrown by Session client

        :return: A more readable/parsable error message
        """
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return "The requested secret " + secret_id + " was not found"
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            return f"The request was invalid due to: {e}"
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            return f"The request had invalid params: {e}"
        elif e.response["Error"]["Code"] == "DecryptionFailure":
            return f"The requested secret can't be decrypted using the provided KMS key: {e}"
        elif e.response["Error"]["Code"] == "InternalServiceError":
            return f"An error occurred on service side: {e}"

        return f"An unknown error occurred: {e}"
