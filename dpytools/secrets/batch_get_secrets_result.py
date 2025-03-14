from typing import Dict, List, Optional

from dpytools.secrets.secret import Secret

_ERRORS_KEY = "Errors"
_SECRETS_KEY = "SecretValues"
_ERROR_MESSAGE_KEY = "Message"
_ERROR_SECRETID_KEY = "SecretId"


class BatchGetSecretsResult:
    """
    Encapsulates logic for parsing AWS SecretsManager batch_get_secret_value response
    """

    def __init__(
        self,
        secret_ids=Optional[List[str]],
        aws_response: Optional[Dict] = None,
        error: Optional[str] = None,
        success: Optional[bool] = None,
    ):
        """
        :param aws_response: Response object from boto3 SecretsManager client
        :param secret_ids: Secret IDs that were used for the request
        :param error: Error message if there was a server error fetching _all_secrets
        :param success: Boolean indicating whether the request was successful or not; will be set automatically, if not passed, based on whether secrets were retrieved etc.
        """
        self.secrets = self.process_aws_response(
            response=aws_response, secret_ids=secret_ids
        )
        self.error = error

        self.success = self.secrets is not None and self.error is None

    def process_aws_response(
        self, secret_ids=Optional[List[str]], response: Optional[Dict] = None
    ) -> Dict[str, Secret]:
        """
        Parse secrets + errors from the batch get secrets AWS response

        :param response: AWS response from boto3 SecretsManager
        :param secret_ids: List of secret IDs that were requested

        :returns: Dictionary where the key is secret ID, and the value is a parsed Secret (success, value, error)
        """
        if response is None:
            return None

        results: Dict[str, Secret] = {}

        self._try_process_successes(response, results)
        self._try_process_errors(response, results)

        if secret_ids is not None:
            self._check_for_missing_secrets(secret_ids=secret_ids, results=results)

        return results

    def _check_for_missing_secrets(
        self, secret_ids: List[str], results: Dict[str, Secret]
    ) -> None:
        """
        Check for any secret IDs that were not returned/parsed in the AWS response, and created
        errored Secret instances in the results obj.
        For any missing secret IDs create a new errored Secret instance in the results.

        :param secret_ids: List of secret ids that were attempted to be fetched
        :param results: Secrets that were parsed from the response

        :returns: Nothing
        """
        for id in secret_ids:
            if id not in results:
                results[id] = Secret(
                    error=f"Secret ID {id} not returned in response", id=id
                )

    def _try_process_errors(self, response: Dict, results: Dict[str, Secret]) -> None:
        """
        Process the "SecretValues" field in the AWS SecretsManager response, and create matching
        Secret instances in the results dictionary

        :param response: AWS SecretsManager response
        :param results: Existing results dictionary (key == secret id, value == parsed Secret instance)

        :returns: None - all Secrets are added to the results dictionary
        """
        if _ERRORS_KEY in response:
            for error_value in response[_ERRORS_KEY]:
                error_secret = Secret(
                    error=error_value[_ERROR_MESSAGE_KEY],
                    id=error_value[_ERROR_SECRETID_KEY],
                )
                results[error_secret.id] = error_secret

    def _try_process_successes(
        self, response: Dict, results: Dict[str, Secret]
    ) -> None:
        """
        Process the "Errors" field in the AWS SecretsManager response, and create matching
        errored Secret instances in the results dictionary

        :param response: AWS SecretsManager response
        :param results: Existing results dictionary (key == secret id, value == parsed Secret instance)

        :returns: None - all errors are added to the results dictionary
        """
        if _SECRETS_KEY in response:
            for value in response[_SECRETS_KEY]:
                secret = Secret(response=value)
                results[secret.id] = secret
