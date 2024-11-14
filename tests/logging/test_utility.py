from datetime import datetime, timedelta
from unittest import mock

from requests import Response

from dpytools.logging.utility import (
    calculate_duration_in_nanoseconds,
    create_error_dict,
    get_content_length,
    get_domain,
    get_end_date,
    get_port,
    get_scheme,
    get_start_date,
    level_to_severity,
)


def test_level_to_severity():
    assert level_to_severity(10) == 3
    assert level_to_severity(20) == 3
    assert level_to_severity(30) == 2
    assert level_to_severity(40) == 1
    assert level_to_severity(50) == 0


def test_create_error_dict():
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_dict = create_error_dict(e)
        assert error_dict[0]["message"] == "Test error"
        assert "stack_trace" in error_dict[0]
        assert "file" in error_dict[0]["stack_trace"]
        assert "function" in error_dict[0]["stack_trace"]
        assert "line" in error_dict[0]["stack_trace"]
        assert "data" in error_dict[0]
        assert "full" in error_dict[0]["data"]


def test_get_scheme():
    assert get_scheme("http://example.com") == "http"
    assert get_scheme("https://example.com") == "https"


def test_get_domain():
    assert get_domain("http://example.com") == "example.com"
    assert get_domain("http://example.com:8080") == "example.com"


def test_get_port():
    assert get_port("http://example.com") == 80
    assert get_port("https://example.com") == 443
    assert get_port("http://example.com:8080") == 8080


def test_get_start_date():
    date_str = "Wed, 21 Oct 2015 07:28:00 GMT"
    assert get_start_date(date_str) == "2015-10-21T07:28:00Z"


def test_get_end_date():
    date_str = "Wed, 21 Oct 2015 07:28:00 GMT"
    time_delta = timedelta(hours=1)
    assert get_end_date(time_delta, date_str) == "2015-10-21T08:28:00Z"


def test_calculate_duration_in_nanoseconds():
    time_delta = timedelta(seconds=1.5)
    date_str = "Wed, 21 Oct 2015 07:28:00 GMT"
    assert calculate_duration_in_nanoseconds(time_delta, date_str) == 1500000000


def test_get_content_length():
    response_with_header = Response()
    response_with_header.headers["Content-Length"] = "12"
    assert get_content_length(response_with_header) == 12

    response_without_header = Response()
    response_without_header._content = b"Test content"
    assert get_content_length(response_without_header) == len(
        response_without_header.content
    )
