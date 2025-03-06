from typing import Optional, Dict, Union
from enum import Enum
import base64    
import json

class SecretType(Enum):
    STRING = 1
    JSON = 2
    BINARY = 4

_STRING_SECRET_KEY = "SecretString"
_BINARY_SECRET_KEY = "SecretBinary"

class Secret:
    """
    Secret value retrieved from AWS Secrets Manager
    """

    def __init__(
        self,
        value: Optional[Dict] = None,
        error: Optional[str] = None,
        success: Optional[bool] = None,
        secret_type: Optional[SecretType] = None
    ):
        self._aws_value = value
        self.error = error
        self.success = self.value is not None and error is None
        self.secret_type = secret_type

    def process_aws_response(self, response: Dict):
        """
        Process AWS Secret Manager response, and set attributes on the class instance as appropriate.
        """
        if response is None:
            self.error = "No response received from AWS"
            return
        
        if "SecretString" in response:
            self._process_string_secret(response)
        elif "SecretBinary" in response:
            self._process_binary_secret(response)

        self.success = True

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
        secret_id = response["Name"]
        if self.try_parse_json(value, secret_id):
            return
        
        self._set_string_value(value)

    def try_parse_json(self, value: str, secret_id: str) -> bool:
        """
        Try parse string secret value as JSON

        :param value: Secret string
        :param secret_id: The ID of the secret

        :return: True if JSON, False otherwise
        """
        try:
            json_dict = json.loads(value)
            
            if secret_id in json_dict:
                self._set_string_value(json_dict[secret_id])
            else:
                self._set_json_value(secret_id, json_dict)

            return True
        # Thrown if string is not valid JSON
        except ValueError as e:
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