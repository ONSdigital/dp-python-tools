import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Optional

import requests
import structlog

from dpytools.logging.utility import (
    calculate_duration_in_nanoseconds,
    create_error_dict,
    get_domain,
    get_end_date,
    get_port,
    get_scheme,
    get_start_date,
    level_to_severity,
)


class DpLogger:
    def __init__(self, namespace: str):
        """
        Simple python logger to create structured logs in keeping
        with https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md

        :param namespace: (required) The namespace for the application.
        """

        class FlushStreamHandler(logging.StreamHandler):
            def emit(self, record):
                super().emit(record)
                self.flush()

        handler = FlushStreamHandler()
        logging.getLogger().addHandler(handler)

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.BoundLogger,
            cache_logger_on_first_use=True,
        )

        self._logger = structlog.get_logger()
        self.namespace = namespace
        self.flush_stdout_after_log_entry = os.environ.get(
            "FLUSH_STDOUT_AFTER_LOG_ENTRY", None
        )

        # Validates the env var being passed in for flush_stdout_after_log_entry
        if self.flush_stdout_after_log_entry is not None:
            assert self.flush_stdout_after_log_entry in [
                "True",
                "true",
                "False",
                "false",
            ], (
                "When using env var FLUSH_STDOUT_AFTER_LOG_ENTRY it must be set to one"
                f" of True, true, False false. Got '{self.flush_stdout_after_log_entry}'"
            )
            self.flush_stdout_after_log_entry = (
                True if self.flush_stdout_after_log_entry in ["True", "true"] else False
            )

    def _log(
        self,
        event,
        level,
        error: Optional[Exception] = None,
        data: Optional[Dict] = None,
        raw: str = None,
        response: Optional[requests.Response] = None,
    ):
        data_dict = data if data is not None else {}
        data_dict["level"] = logging.getLevelName(level)

        # Match DP logging structure
        # https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md

        if response is not None:
            r_dict = {
                "method": response.request.method,
                "scheme": get_scheme(response.url),
                "host": get_domain(response.url),
                "port": get_port(response.url),
                "path": response.request.path_url,
                "status_code": response.status_code,
                "started_at": get_start_date(response.headers["Date"]),
                "ended_at": get_end_date(response.elapsed, response.headers["Date"]),
                "duration": calculate_duration_in_nanoseconds(
                    response.elapsed, response.headers["Date"]
                ),
                "response_content_length": len(response.content),
            }
        else:
            r_dict = None

        log_event = {
            "severity": level_to_severity(level),
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "namespace": self.namespace,
            "trace_id": "not-implemented",
            "span_id": "not-implemented",
            "data": data_dict,
            "response_dict": r_dict,
            "raw": raw,
            "errors": create_error_dict(error) if error is not None else None,
        }
        self._logger.log(**log_event)
        if self.flush_stdout_after_log_entry:
            sys.stdout.flush()

    def debug(
        self,
        event: str,
        raw: str = None,
        data: Dict = None,
        response: requests.Response = None,
    ):
        """
        Log at the debug level.

        :param event: The event description.
        :param raw: Raw log data for a third party library.
        :param data: Additional context data such as arbitrary key-value pairs that may be of use in providing context.
        :param response: Optional HTTP response to include in the log.
        """
        self._log(event, logging.DEBUG, raw=raw, data=data, response=response)

    def info(
        self,
        event: str,
        raw: str = None,
        data: Dict = None,
        response: requests.Response = None,
    ):
        """
        Log at the info level.

        :param event: The event description.
        :param raw: Raw log data for a third party library.
        :param data: Additional context data such as arbitrary key-value pairs that may be of use in providing context.
        """
        self._log(event, logging.INFO, raw=raw, data=data)

    def warning(
        self,
        event: str,
        raw: str = None,
        data: Dict = None,
        response: requests.Response = None,
    ):
        """
        Log at the warning level.

        :param event: The event description.
        :param raw: Raw log data for a third party library.
        :param data: Additional context data such as arbitrary key-value pairs that may be of use in providing context.
        :param response: Optional HTTP response to include in the log.
        """
        self._log(event, logging.WARNING, raw=raw, data=data, response=response)

    def error(
        self,
        event: str,
        error: Optional[Exception] = None,
        raw: str = None,
        data: Dict = None,
        response: requests.Response = None,
    ):
        """
        Log at the error level.

        :param event: The event description.
        :param error: A python Exception.
        :param raw: Raw log data for a third party library.
        :param data: Additional context data such as arbitrary key-value pairs that may be of use in providing context.
        :param response: Optional HTTP response to include in the log.
        """
        self._log(
            event, logging.ERROR, error=error, raw=raw, data=data, response=response
        )

    def critical(
        self,
        event: str,
        error: Exception,
        raw: str = None,
        data: Dict = None,
        response: requests.Response = None,
    ):
        """
        IMPORTANT: You should only be logging at the critical level during
        application failure, i.e. if your app is in the process of failing
        over you should log at critical level.

        Log at the critical level.

        :param event: The event description.
        :param error: A python Exception.
        :param raw: Raw log data for a third party library.
        :param data: Additional context data such as arbitrary key-value pairs that may be of use in providing context.
        :param response: Optional HTTP response to include in the log.
        """
        self._log(
            event, logging.CRITICAL, error=error, raw=raw, data=data, response=response
        )
