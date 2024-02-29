from pathlib import Path
from dpytools.http.upload import UploadClient
from tempfile import TemporaryDirectory


# TODO Use vcrpy to record HTTP request content
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
        temp_file_paths_list = UploadClient()._create_temp_chunks(
            csv_path="tests/test_cases/countries.csv", output_path=temp_dir_path
        )
        assert len(temp_file_paths_list) == 2
        assert "temp-file-part-1" in temp_file_paths_list[0]
