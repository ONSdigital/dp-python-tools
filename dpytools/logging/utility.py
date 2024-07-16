import sys
import traceback
import subprocess
from typing import Dict, List


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


def create_error_dict(error: Exception) -> List[Dict]:
    """
    Take a python Exception and create a sub dict/document
    matching DP logging standards expression of a captured
    error.

    https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md#error-event-data
    """

    tb = traceback.extract_tb(error.__traceback__)

    if not tb:
        return [{"error_message": str(error), "error_trace": ""}]

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

    # Listify in keeping with expected DP logging structures
    return [error_dict]

def get_commit_ID():
    try:
        commit_id=subprocess.check_output(["git", "log", "-1", "--format=%H"]).strip().decode("utf-8")
        return commit_id
    except subprocess.CalledProcessError as err:
        print("Error while fetching commit ID", err)
        return None