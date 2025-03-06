import boto3
from botocore.exceptions import ClientError

from dpytools.secrets.secret import Secret

_CLIENT_NAME = "secretsmanager"

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
            return Secret(error=error)
        except Exception as e:
            return Secret(
                error=f"An unknown error occurred retrieving the secret {secret_id} from AWS Secrets Manager: {e}"
            )

        if get_secret_value_response is None:
            return Secret(error="None value for get_secret_value_response")

        return Secret(value=get_secret_value_response)

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
