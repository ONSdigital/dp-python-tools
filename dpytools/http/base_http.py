import backoff
import requests
from requests.exceptions import HTTPError

from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


# Function to log retry attempts
def log_retry(details):
    logger.warning(f"Request failed, retrying... Attempt #{details['tries']}")


# We don't want to retry on 404 as we are retrying a non-existent resource.
# To test whether a dataset exists we query a specific url and it will return a 404 if it does not exist.
def giveup_on_404(e: HTTPError) -> bool:
    """
    Returns Boolean based on whether status code is 404 or not
    """
    return e.response.status_code == 404


class BaseHttpClient:
    # GET request method with exponential backoff
    @backoff.on_exception(
        backoff.expo, HTTPError, max_time=30, on_backoff=log_retry, giveup=giveup_on_404
    )
    def get(self, url, *args, **kwargs):
        """
        Sends a GET request to the specified URL with optional extra arguments.

        This method is a thin wrapper around `requests.get()`. Any additional arguments
        are passed directly to `requests.get()`. For more information on the available
        arguments, refer to the `requests.get()` documentation:
        https://docs.python-requests.org/en/latest/api/#requests.get

        Args:
            url (str): The URL to send the GET request to.
            *args: Optional positional arguments passed to `requests.get()`.
            **kwargs: Optional keyword arguments passed to `requests.get()`.

        Returns:
            Response: The Response object from `requests.get()`.
        Raises:
            HTTPError: If the request fails for a network-related reason.
        """
        return self._handle_request("GET", url, *args, **kwargs)

    # POST request method with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        HTTPError,
        max_time=30,
        on_backoff=log_retry,
    )
    def post(self, url, *args, **kwargs):
        """
        Sends a POST request to the specified URL with optional extra arguments.

        This method is a thin wrapper around `requests.post()`. Any additional arguments
        are passed directly to `requests.post()`. For more information on the available
        arguments, refer to the `requests.post()` documentation:
        https://docs.python-requests.org/en/latest/api/#requests.post

        Args:
            url (str): The URL to send the POST request to.
            *args: Optional positional arguments passed to `requests.post()`.
            **kwargs: Optional keyword arguments passed to `requests.post()`.

        Returns:
            Response: The Response object from `requests.post()`.

        Raises:
            HTTPError: If the request fails for a network-related reason.
        """
        return self._handle_request("POST", url, *args, **kwargs)

    # PUT request method with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        HTTPError,
        max_time=30,
        on_backoff=log_retry,
    )
    def put(self, url, *args, **kwargs):
        """
        Sends a PUT request to the specified URL with optional extra arguments.

        This method is a thin wrapper around `requests.put()`. Any additional arguments
        are passed directly to `requests.put()`. For more information on the available
        arguments, refer to the `requests.put()` documentation:
        https://docs.python-requests.org/en/latest/api/#requests.post

        Args:
            url (str): The URL to send the PUT request to.
            *args: Optional positional arguments passed to `requests.put()`.
            **kwargs: Optional keyword arguments passed to `requests.put()`.

        Returns:
            Response: The Response object from `requests.put()`.

        Raises:
            HTTPError: If the request fails for a network-related reason.
        """
        return self._handle_request("PUT", url, *args, **kwargs)

    # Method to handle requests
    def _handle_request(self, method, url, *args, **kwargs) -> requests.Response:
        data = {"method": method, "url": url}

        if "json" in kwargs:
            data["json"] = kwargs["json"]
        logger.info(f"Sending {method} request to {url}", data=data)
        response = requests.request(method, url, *args, **kwargs)
        return response
