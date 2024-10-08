from pathlib import Path
from typing import Optional, Union

from dpytools.http.upload.base_upload import BaseUploadClient

from ..token_auth import TokenAuth

# Dev note:

# At time of writing (17/5/2024) there's two endpoints supported
# by the uplaod service.

# 1. /upload
# 2. /upload-new

# Putting aside the wisdom of "new" we do need to support both of
# these options so have by neceessity adopted this nomanclature.


class UploadServiceClient(BaseUploadClient):
    def __init__(self, upload_url: str, backoff_max=30):
        super().__init__(upload_url=upload_url, backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)

    def upload_csv(
        self,
        csv_path: Union[Path, str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload csv files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        self._upload(csv_path, "text/csv", chunk_size)

    def upload_sdmx(
        self,
        sdmx_path: Union[Path, str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload sdmx files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        self._upload(sdmx_path, "application/xml", chunk_size)

    def upload_json(
        self,
        json_path: Union[Path, str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload json files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `json_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        self._upload(json_path, "application/json", chunk_size)

    def upload_new_csv(
        self,
        csv_path: Union[Path, str],
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        license: Optional[str] = None,
        license_url: Optional[str] = None,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload csv files to the DP Upload Service `/upload-new` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        `alias_name` and `title` are optional arguments. If these are not explicitly provided, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension - e.g. if the filename is "data.csv", `alias_name` defaults to "data.csv" and `title` defaults to "data".
        """
        self._upload_new(
            csv_path,
            "text/csv",
            alias_name,
            title,
            license,
            license_url,
            chunk_size,
        )

    def upload_new_sdmx(
        self,
        sdmx_path: Union[Path, str],
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        license: Optional[str] = None,
        license_url: Optional[str] = None,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload sdmx files to the DP Upload Service `/upload-new` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        `alias_name` and `title` are optional arguments. If these are not explicitly provided, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension - e.g. if the filename is "data.csv", `alias_name` defaults to "data.csv" and `title` defaults to "data".
        """
        self._upload_new(
            sdmx_path,
            "application/xml",
            alias_name,
            title,
            license,
            license_url,
            chunk_size,
        )

    def upload_new_json(
        self,
        json_path: Union[Path, str],
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        license: Optional[str] = None,
        license_url: Optional[str] = None,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload json files to the DP Upload Service `/upload-new` endpoint. The file to be uploaded (located at `json_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        `alias_name` and `title` are optional arguments. If these are not explicitly provided, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension - e.g. if the filename is "data.json", `alias_name` defaults to "data.json" and `title` defaults to "data".
        """
        self._upload_new(
            json_path, 
            "application/json", 
            alias_name, 
            title,
            license,
            license_url, 
            chunk_size,
        )
