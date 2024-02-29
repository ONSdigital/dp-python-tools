import datetime
import os

import requests

from dpytools.http.base import BaseHttpClient


class UploadClient(BaseHttpClient):
    def __init__(
        self,
        upload_url: str = "",
        headers: dict = {"X-Florence-Token": ""},
    ):
        super().__init__()
        # TODO Actual values for `upload_url` and `headers` (see `POST` request  in `upload_new()`)
        self.upload_url = upload_url
        self.headers = headers

    def upload_new(
        self, csv_path: str, output_path: str = None, is_publishable: bool = False
    ) -> str:
        """
        Upload files to the DP Upload Service. Files are chunked (default chunk size 5242880 bytes)
        """
        # Get size of file to be uploaded
        resumable_total_size = str(os.path.getsize(csv_path))

        # Get file name from file path
        resumable_file_name = csv_path.split("/")[-1]

        # Get timestamp to create `path` value in `POST` params
        timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

        # Create file chunks
        file_chunks = self._create_temp_chunks(
            csv_path=csv_path, output_path=output_path, chunk_size=1000
        )

        resumable_chunk_number = 1

        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}
                # Construct `POST` request params for each file chunk
                params = {
                    "resumableFilename": resumable_file_name,
                    # TODO Check `path` value (replaces resumableIdentifier?)
                    # Description: The path to the file being stored. Note that this will be part of the AWS S3 bucket name so should adhere to the S3 bucket naming rules
                    "path": f"{timestamp}-{resumable_file_name.replace('.', '-')}",
                    "isPublishable": is_publishable,
                    # TODO delete `collectionId` as optional for upload?
                    "collectionId": "optional for upload, required before publishing",
                    # TODO `title` value (optional)
                    "title": "title value",
                    "resumableTotalSize": resumable_total_size,
                    # TODO `resumableType` - accept other types?
                    "resumableType": "text/csv",
                    # TODO `licence` value
                    "licence": "licence value",
                    # TODO `licenceUrl` value
                    "licenceUrl": "licenceUrl value",
                    "resumableChunkNumber": resumable_chunk_number,
                    "resumableTotalChunks": len(file_chunks),
                }

                # Submit `POST` request to `upload_url`
                response = self.post(
                    url=self.upload_url,
                    headers=self.headers,
                    params=params,
                    files=file,
                    verify=True,
                )
                if response.status_code != 200:
                    raise Exception(
                        f"{self.upload_url} returned error {response.status_code}"
                    )

                print(f"Temp file number {resumable_chunk_number} posted")
                resumable_chunk_number += 1

        # TODO Check s3_key
        s3_key = params["path"]

        # TODO Check staging S3 URL
        s3_url = f"https://s3-eu-west-2.amazonaws.com/ons-dp-staging-publishing-uploaded-datasets/{s3_key}"

        self._delete_temp_chunks(file_chunks)
        print("Upload to s3 complete")

        return s3_url

    def _create_temp_chunks(
        self, csv_path: str, output_path: str = None, chunk_size: int = 5242880
    ) -> list[str]:
        """
        Chunks up the data into text files, returns list of temp files
        """
        if output_path is None:
            output_path = "/".join(csv_path.split("/")[:-1]) + "/"
        if output_path == "/":
            output_path = ""
        chunk_number = 1
        temp_file_paths_list = []
        with open(csv_path, "rb") as f:
            chunk = f.read(chunk_size)
            while chunk:
                temp_file_path = f"{output_path}-temp-file-part-{str(chunk_number)}"
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(chunk)
                    temp_file_paths_list.append(temp_file_path)
                chunk_number += 1
                chunk = f.read(chunk_size)
        return temp_file_paths_list

    def _delete_temp_chunks(self, temporary_files: list):
        """
        Deletes the temporary chunks that were uploaded
        """
        for file in temporary_files:
            os.remove(file)

    # def _get_access_token(self):
    #     # gets florence access token
    #     try:  # so that token isn't generate for each __init__
    #         if self.access_token:
    #             pass
    #     except:
    #         # getting credential from environment variables
    #         email, password = self._get_credentials()
    #         login = {"email": email, "password": password}

    #         r = requests.post(self.login_url, json=login, verify=True)
    #         if r.status_code == 200:
    #             access_token = r.text.strip('"')
    #             self.access_token = access_token
    #         else:
    #             raise Exception(f"Token not created, returned a {r.status_code} error")

    # def _get_credentials(self):
    #     email = os.getenv("FLORENCE_EMAIL")
    #     password = os.getenv("FLORENCE_PASSWORD")
    #     if email and password:
    #         pass
    #     else:
    #         print("Florence credentials not found in environment variables")
    #         print("Will need to be passed")

    #         email = input("Florence email: ")
    #         password = input("Florence password: ")
    #     return email, password


# get platform name
# hack to tell if using on network machine - windows implies on network
# if sys.platform.lower().startswith("win"):
#     verify = False
#     operating_system = "windows"
#     requests.packages.urllib3.disable_warnings()
# else:
#     verify = True
#     operating_system = "not windows"
