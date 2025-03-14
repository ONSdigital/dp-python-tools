import base64
import json
from enum import Enum
from typing import Dict, Optional, Union


class SecretType(Enum):
    STRING = 1
    JSON = 2
    BINARY = 4


_STRING_SECRET_KEY = "SecretString"
_BINARY_SECRET_KEY = "SecretBinary"
_SECRET_NAME_KEY = "Name"

_NO_SECRET_ERROR = "No secret was found in the AWS response"
_NO_RESPONSE_ERROR = "No response received from AWS"


class Secret:
    """
    Secret value retrieved from AWS Secrets Manager
    """

    def __init__(
        self,
        response: Optional[Dict] = None,
        error: Optional[str] = None,
        success: Optional[bool] = None,
        secret_type: Optional[SecretType] = None,
        id: Optional[str] = None,
    ):
        """
        :param response: AWS response for retrieving the secret
        :param error: Parsed error message from retrieving the secret (if any)
        :param success: Whether this secret was successfully retrieved or not; is automatically set if not provided
        :param secret_type: Type of secret value (string, JSON, bytes)
        :param id: The secret ID/name
        """
        self.value = None
        self.error = None

        self.id = id
        self.secret_type = secret_type

        self.process_aws_response(response, error)
        self.success = self.value is not None and error is None

    def process_aws_response(self, response: Optional[Dict], error: Optional[str]):
        """
        Process AWS Secret Manager response, and set attributes on the class instance as appropriate.

        :param response: AWS SecretsManager response
        :parma error: Parsed error message
        """
        if error is not None:
            self.error = error
            return

        if response is None:
            self.error = _NO_RESPONSE_ERROR
            return

        self._set_secret_name(response)

        if "SecretString" in response:
            self._process_string_secret(response)
        elif "SecretBinary" in response:
            self._process_binary_secret(response)
        else:
            self.error = _NO_SECRET_ERROR

    def _process_binary_secret(self, response: Dict):
        """
        Get binary secret value and Base64 decode
        """
        self._set_binary_value(base64.b64decode(response[_BINARY_SECRET_KEY]))

    def _process_string_secret(self, response: Dict):
        """
        Get string secret and try parse as JSON

        :param response: AWS Secret Manager response
        """
        value = response[_STRING_SECRET_KEY]
        if self.try_parse_json(value):
            return

        self._set_string_value(value)

    def try_parse_json(self, value: str) -> bool:
        """
        Try parse string secret value as JSON

        :param value: Secret string
        :param secret_id: The ID of the secret

        :return: True if JSON, False otherwise
        """
        try:
            json_dict = json.loads(value)

            if self.id is not None and self.id in json_dict:
                self._set_string_value(json_dict[self.id])
            else:
                self._set_json_value(json_dict)

            return True
        # Thrown if string is not valid JSON
        except ValueError:
            return False

    def _set_json_value(self, dict: Dict):
        self._set_value(dict, SecretType.JSON)

    def _set_string_value(self, value: str):
        self._set_value(value, SecretType.STRING)

    def _set_binary_value(self, value: bytes):
        self._set_value(value, SecretType.BINARY)

    def _set_value(self, value: Union[str, Dict, bytes], type: SecretType):
        self.value = value
        self.secret_type = type

    def _set_secret_name(self, response: Dict):
        """
        Retrieve the secret ID from the AWS response and set id attribute to the value
        """
        if _SECRET_NAME_KEY in response:
            self.id = response[_SECRET_NAME_KEY]
