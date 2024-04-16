import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import structlog

from dpytools.logging.utility import create_error_dict, level_to_severity


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

    def _log(
        self,
        event,
        level,
        error: Optional[List] = None,
        data: Optional[Dict] = None,
        raw: str = None,
    ):
        data_dict = data if data is not None else {}
        data_dict["level"] = logging.getLevelName(level)

        log_event = {
            "severity": level_to_severity(level),
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "namespace": self.namespace,
            "trace_id": "not-implemented",
            "span_id": "not-implemented",
            "data": data_dict,
            "raw": raw,
            "error": create_error_dict(error) if error is not None else None,
        }

        self._logger.log(**log_event)

    def debug(self, event: str, raw: str = None, data: Dict = None):
        """
        Log at the debug level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 10, raw=raw, data=data)

    def info(self, event: str, raw: str = None, data: Dict = None):
        """
        Log at the info level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 20, raw=raw, data=data)

    def warning(self, event: str, raw: str = None, data: Dict = None):
        """
        Log at the warning level.

        event: the thing that's happened, a simple short english statement
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 30, raw=raw, data=data)

    def error(self, event: str, error: Exception, raw: str = None, data: Dict = None):
        """
        Log at the error level.

        event: the thing that's happened, a simple short english statement
        error: a python Exception
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 40, error=error, raw=raw, data=data)

    def critical(
        self, event: str, error: Exception, raw: str = None, data: Dict = None
    ):
        """
        IMPORTANT: You should only be logging at the critical level during
        application failure, i.e if you're app is not in the process of falling
        over you should not be logging a critical.

        Log at the critical level.

        event: the thing that's happened, a simple short english statement
        error: a caught python Exceotion
        raw  : a raw string of any log messages captured for a third party library
        data : arbitrary key-value pairs that may be of use in providing context
        """
        self._log(event, 50, error=error, raw=raw, data=data)
