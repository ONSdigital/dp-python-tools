import pytest
import vcr
import requests
import urllib.request
from dpytools.http.upload import UploadClient
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory


# TODO Use vcr
# https://vcrpy.readthedocs.io/en/latest/usage.html
# https://pytest-vcr.readthedocs.io/en/latest/
def test_upload_new():
    with TemporaryDirectory() as temp_dir_path:
        s3_url = UploadClient().upload_new(
            csv_path="tests/test_cases/countries.csv", output_path=temp_dir_path
        )
        assert s3_url == ""
        # assert temp files deleted


def test_create_temp_chunks():
    with TemporaryDirectory() as temp_dir_path:
        temp_files = UploadClient()._create_temp_chunks(
            csv_path="tests/test_cases/countries.csv", output_path=temp_dir_path
        )
        assert len(temp_files) == 2
        assert "temp-file-part-1" in temp_files[0]


# @pytest.mark.vcr()
# def test_iana():
#     response = urllib.request.urlopen("http://www.iana.org/domains/reserved").read()
#     assert b"Example domains" in response
