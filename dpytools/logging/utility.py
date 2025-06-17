import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict
from urllib.parse import urlparse

from requests import Response


def level_to_severity(level: int) -> int:
    """
    Helper to convert logging level to severity, please
    see: https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md#severity-levels
    """
    if level > 40:
        return 0
    elif level > 30:
        return 1
    elif level > 20:
        return 2
    else:
        return 3


def create_error_dict(error: Exception) -> Dict:
    """
    Take a python Exception and create a sub dict/document
    matching DP logging standards expression of a captured
    error.

    https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md#error-event-data
    """

    tb = traceback.extract_tb(error.__traceback__)

    if not tb:
        return {"error_message": str(error), "error_trace": ""}

    # Get the last exception where exceptions are chained.
    last_call = tb[-1]

    exc_type, exc_value, exc_traceback = sys.exc_info()
    formatted_traceback = traceback.format_exception(exc_type, exc_value, exc_traceback)

    error_dict = {
        "message": str(error),
        "stack_trace": {
            "file": last_call.filename,
            "function": last_call.name,
            "line": last_call.lineno,
        },
        "data": {"full": formatted_traceback},
    }

    return error_dict


def get_scheme(url: str) -> str:
    """This function will return the scheme from the provided url."""

    index = url.find("/")
    scheme = url[0 : index - 1]
    return scheme


def get_domain(url: str) -> str:
    """This function will return the domain name from the provided url."""
    # Parsing url to extract the domain name
    parsed_url = urlparse(url)

    # Getting the domain name
    domain = parsed_url.netloc.split(":")[0]
    return domain


def get_port(url: str) -> int:
    """This function will return the port number form the provided url."""
    # Parsing url
    parsed_url = urlparse(url)

    # checking if the port was give if not checking scheme for port number
    if parsed_url.port is None:
        if parsed_url.scheme == "http":
            return 80
        else:
            return 443
    else:
        return parsed_url.port


def get_start_date(date: str) -> str:
    strp_time = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")

    return strp_time.isoformat() + "Z"


def get_end_date(time_delta: timedelta, date: str) -> str:
    """This function will calculate the end_date by adding the duration to the start date."""

    strp_time = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
    end_date = strp_time + time_delta

    return end_date.isoformat() + "Z"


def calculate_duration_in_nanoseconds(time_delta: timedelta, date: str) -> float:
    """This function will calculate the duration in nanoseconds."""
    strp_time = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
    end_date = strp_time + time_delta
    duration = end_date - strp_time
    return duration.total_seconds() * 1_000_000_000


def get_content_length(res: Response) -> int:
    """
    This function will try to get the 'Content-Lenght'
    if there is noone it will return a default 0.
    """
    try:
        content_length = res.headers["Content-Length"]
        return int(content_length)
    except KeyError:
        return len(res.content)
