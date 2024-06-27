import logging
import os
import sys
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

import structlog

from dpytools.logging.utility import (
    create_error_dict,
    level_to_severity,
    get_domain,
    get_scheme,
    get_domain,
    get_port,
    get_start_date,
    get_end_date,
    calculate_duration_in_nanoseconds)

class DpLogger:
    def __init__(self, namespace: str):
        """
        Simple python logger to create structured logs in keeping
        with https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md

        namespace: (required) the namespace for the app in question
        """

        logging.getLogger().addHandler(logging.StreamHandler())

        processors = [structlog.processors.JSONRenderer()]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.BoundLogger,
            cache_logger_on_first_use=True,
        )

        self._logger = structlog.get_logger()
        self.namespace = namespace
        self.flush_stdout_after_log_entry = os.environ.get(
            "FLUSH_STOUT_AFTER_LOG_ENTRY", None
        )

        # Polics the env var being passed in for flush_stdout_after_log_entry
        if self.flush_stdout_after_log_entry is not None:
            assert self.flush_stdout_after_log_entry in [
                "True",
                "true",
                "False",
                "false",
            ], (
                "When using env var FLUSH_STOUT_AFTER_LOG_ENTRY it must be set to one"
                f" of True, true, False false. Got '{self.flush_stdout_after_log_entry}'"
            )
            self.flush_stdout_after_log_entry = (
                True if self.flush_stdout_after_log_entry in ["True", "true"] else False
            )

    def _log(
        self,
        event,
        level,
        error: Optional[List] = None,
        data: Optional[Dict] = None,
        raw: str = None,
        response = Optional[requests.Response],
    ):
        data_dict = data if data is not None else {}
        data_dict["level"] = logging.getLevelName(level)

        # match dp logging structue
        # https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md
        log_event = {
            "severity": level_to_severity(level),
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "namespace": self.namespace,
            "trace_id": "not-implemented",
            "span_id": "not-implemented",
            "data": data_dict,
            "raw": raw,
            "errors": create_error_dict(error) if error is not None else None,
        }

        r_dict = {
            "method": response.request.method,
            "scheme": get_scheme(response.url),
            "host": get_domain(response.url),
            "port": get_port(response.url),
            "path": response.request.path_url,
            "status_code" : response.status_code,
            "started_at":get_start_date(response.headers["Date"]),
            "ended_at":get_end_date(response.elapsed, response.headers["Date"]),
            "duration": calculate_duration_in_nanoseconds(response.elapsed, response.headers["Date"]),
            "response_content_length":len(response.content)
            }

        reponse_dict = r_dict if response is not None else {}

        self._logger.log(**log_event)

        if self.flush_stdout_after_log_entry is True:
            sys.stdout.flush()

    def debug(self, event: str, raw: str = None, data: Dict = None, response: requests.Response = None):
        """
        Log at the debug level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 10, raw=raw, data=data, response=response)

    def info(self, event: str, raw: str = None, data: Dict = None, response: requests.Response = None):
        """
        Log at the info level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 20, raw=raw, data=data)

    def warning(self, event: str, raw: str = None, data: Dict = None, response: requests.Response = None):
        """
        Log at the warning level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 30, raw=raw, data=data, response=response)

    def error(self, event: str, error: Exception, raw: str = None, data: Dict = None, response: requests.Response = None):
        """
        Log at the error level.

        event: the thing that's happened, a simple short english statement
        error: a python Exception
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 40, error=error, raw=raw, data=data, response=response)

    def critical(
        self, event: str, error: Exception, raw: str = None, data: Dict = None, response: requests.Response = None
    ):
        """
        IMPORTANT: You should only be logging at the critical level during
        application failure, i.e if you're app is not in the process of falling
        over you should not be logging a critical.

        Log at the critical level.

        event: the thing that's happened, a simple short english statement
        error: a caught python Exception
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 50, error=error, raw=raw, data=data, response=response)
