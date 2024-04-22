import json
from typing import Dict

import pytest

from dpytools.logging.logger import DpLogger


@pytest.fixture
def logger():
    logger = DpLogger("testing")
    return logger


def _get_captured_log(capfd) -> Dict:
    """
    Capture the structured (json) log going to
    standard out and read it into a dict so
    we can check its contents.
    """
    stdout, _ = capfd.readouterr()
    return json.loads(stdout)


def _view_log(log: dict) -> str:
    """
    Helper to convert our structred log dict
    into a well formatted string in the
    event of failed assertions.
    """
    return json.dumps(log, indent=2)


def test_debug_log_simple(logger: DpLogger, capfd):
    """
    Test a simple debug log contains the expected data
    """
    message = "I am a message"

    logger.debug(message)

    log: Dict = _get_captured_log(capfd)
    assert log["event"] == message, _view_log(log)
    assert log["namespace"] == "testing", _view_log(log)
    assert log["severity"] == 3, _view_log(log)
    assert log["raw"] is None, _view_log(log)
    assert log["data"]["level"] == "DEBUG", _view_log(log)


def test_debug_log_complex(logger: DpLogger, capfd):
    """
    Test a complex debug log contains the expected data
    """
    message = "I am a message"
    raw = "arbitrary string data"
    data = {"ghostbusters": ["Ray", "Egon", "Peter", "Winston"]}

    logger.debug(message, raw=raw, data=data)

    log: Dict = _get_captured_log(capfd)
    assert log["event"] == message, _view_log(log)
    assert log["namespace"] == "testing", _view_log(log)
    assert log["severity"] == 3, _view_log(log)
    assert log["raw"] == raw, _view_log(log)
    assert log["data"]["level"] == "DEBUG", _view_log(log)
    assert log["data"]["ghostbusters"] == data["ghostbusters"], _view_log(log)


def test_info_log_complex(logger: DpLogger, capfd):
    """
    Test a complex info log contains the expected data
    """
    message = "I am a message"
    raw = "arbitrary string data"
    data = {"ghostbusters": ["Ray", "Egon", "Peter", "Winston"]}

    logger.info(message, raw=raw, data=data)

    log: Dict = _get_captured_log(capfd)
    assert log["event"] == message, _view_log(log)
    assert log["namespace"] == "testing", _view_log(log)
    assert log["severity"] == 3, _view_log(log)
    assert log["raw"] == raw, _view_log(log)
    assert log["data"]["level"] == "INFO", _view_log(log)
    assert log["data"]["ghostbusters"] == data["ghostbusters"], _view_log(log)


def test_warning_log_complex(logger: DpLogger, capfd):
    """
    Test a complex warning log contains the expected data
    """
    message = "I am a message"
    raw = "arbitrary string data"
    data = {"ghostbusters": ["Ray", "Egon", "Peter", "Winston"]}

    logger.warning(message, raw=raw, data=data)

    log: Dict = _get_captured_log(capfd)
    assert log["event"] == message, _view_log(log)
    assert log["namespace"] == "testing", _view_log(log)
    assert log["severity"] == 2, _view_log(log)
    assert log["raw"] == raw, _view_log(log)
    assert log["data"]["level"] == "WARNING", _view_log(log)
    assert log["data"]["ghostbusters"] == data["ghostbusters"], _view_log(log)


def test_error_log_complex(logger: DpLogger, capfd):
    """
    Test a complex error log contains the expected data
    """
    message = "I am a message"
    err_message = "I went boom"
    raw = "arbitrary string data"
    data = {"ghostbusters": ["Ray", "Egon", "Peter", "Winston"]}

    try:
        raise ValueError(err_message)
    except Exception as err:
        logger.error(message, err, raw=raw, data=data)

        log: Dict = _get_captured_log(capfd)
        assert log["event"] == message, _view_log(log)
        assert log["namespace"] == "testing", _view_log(log)
        assert log["severity"] == 1, _view_log(log)
        assert log["raw"] == raw, _view_log(log)
        assert log["data"]["level"] == "ERROR", _view_log(log)
        assert log["data"]["ghostbusters"] == data["ghostbusters"], _view_log(log)
        assert log["error"][0]["message"] == err_message, _view_log(log)
        assert log["error"][0]["stack_trace"]["file"].endswith(
            "test_logger.py"
        ), _view_log(log)
        assert log["error"][0]["stack_trace"]["line"] == 124, _view_log(log)
        assert (
            log["error"][0]["stack_trace"]["function"] == "test_error_log_complex"
        ), _view_log(log)


def test_critical_log_complex(logger: DpLogger, capfd):
    """
    Test a critical error log contains the expected data
    """
    message = "I am a message"
    err_message = "I went boom"
    raw = "arbitrary string data"
    data = {"ghostbusters": ["Ray", "Egon", "Peter", "Winston"]}

    try:
        raise ValueError(err_message)
    except Exception as err:
        logger.critical(message, err, raw=raw, data=data)

        log: Dict = _get_captured_log(capfd)
        assert log["event"] == message, _view_log(log)
        assert log["namespace"] == "testing", _view_log(log)
        assert log["severity"] == 0, _view_log(log)
        assert log["raw"] == raw, _view_log(log)
        assert log["data"]["level"] == "CRITICAL", _view_log(log)
        assert log["data"]["ghostbusters"] == data["ghostbusters"], _view_log(log)
        assert log["error"][0]["message"] == err_message, _view_log(log)
        assert log["error"][0]["stack_trace"]["file"].endswith(
            "test_logger.py"
        ), _view_log(log)
        assert log["error"][0]["stack_trace"]["line"] == 154, _view_log(log)
        assert (
            log["error"][0]["stack_trace"]["function"] == "test_critical_log_complex"
        ), _view_log(log)
