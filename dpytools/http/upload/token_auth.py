import os
from datetime import datetime, timedelta
from typing import Dict

from dpytools.http.base import BaseHttpClient
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class TokenAuth(BaseHttpClient):
    def __init__(self, backoff_max=30):
        super().__init__(backoff_max=backoff_max)
        # RE auth, there'd two modes
        # 1. Service account mode
        # 2. User account mode
        # The headers used are slightly different and
        # user account mode required refreshing the auth
        # token before a 15 minute timeout happens
        # (service account auth doesn't time out)

        self.service_token = os.environ.get("SERVICE_TOKEN_FOR_UPLOAD", None)
        if self.service_token is None:
            self.set_user_tokens()

    def set_user_tokens(self):
        """
        When using user auth we need to use florence username and password
        to create a florence token.

        We also need to get the refresh token so we can extend the token
        lifespan beyond the 15 minute timeout where necessary.
        """

        self.florence_user = os.environ.get("FLORENCE_USER", None)
        self.florence_password = os.environ.get("FLORENCE_PASSWORD", None)
        self.identity_api_url = os.environ.get("IDENTITY_API_URL", None)

        assert (
            self.florence_user is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var FLORENCE_USER must be provided"
        assert (
            self.florence_password is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var FLORENCE_PASSOWRD must be provided"
        assert (
            self.identity_api_url is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var IDENTITY_API_URL must be provided"

        # https://github.com/ONSdigital/dp-identity-api/blob/develop/swagger.yaml
        token_url = f"{self.identity_api_url}/tokens"
        response = self.post(
            token_url,
            json={"email": self.florence_user, "password": self.florence_password},
        )
        if response.status_code == 201:
            response_headers = response.headers

            self.refresh_token = response_headers["Refresh"]
            self.token_creation_time = datetime.now()

            self.auth_token = response_headers["Authorization"]
            self.id_token = response_headers["ID"]
        else:
            err = Exception("Failed to create user tokens")
            logger.error(
                "Failed to create user tokens",
                err,
                data={
                    "identity_api_url": self.identity_api_url,
                    "token_url": token_url,
                    "response_staus_code": response.status_code,
                    "response_content": response.content,
                },
            )
            raise err

    def get_auth_header(self) -> Dict[str, str]:
        """
        Given a dictionary of params, set the auth header based on the
        auth mode in use.
        """

        # Using service account
        if self.service_token:
            return {"Authorization": f"Bearer {self.service_token}"}

        # Using user account
        # If the token is more than 10 minutes old refresh it
        # https://github.com/ONSdigital/dp-identity-api/blob/develop/swagger.yaml
        if (datetime.now() - self.token_creation_time) > timedelta(minutes=10):
            self.refresh_user_token()

        return {"X-Florence-Token": self.auth_token, "ID": self.id_token}

    def refresh_user_token(self):
        """
        Refreshes the user token by sending a PUT request to the
        Identity API's token endpoint with the current refresh token
        and ID token.
        """
        token_refresh_url = f"{self.identity_api_url}/tokens/self"
        response = self.put(
            token_refresh_url,
            json={"Refresh": self.refresh_token, "ID": self.id_token},
        )

        if response.status_code == 201:
            self.auth_token = response.headers["Authorization"]
            self.id_token = response.headers["ID"]
        else:
            err = Exception(
                f"Refreshing token failed, returned a {response.status_code} error"
            )
            logger.error(
                "Could not refresh user auth token",
                err,
                data={
                    "token_refresh_url": token_refresh_url,
                    "response_status_code": response.status_code,
                    "response_content": response.content,
                },
            )
            raise err
