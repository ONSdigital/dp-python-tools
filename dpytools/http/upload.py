import datetime
import os

from dpytools.http.base import BaseHttpClient

# get platform name
# hack to tell if using on network machine - windows implies on network
# if sys.platform.lower().startswith("win"):
#     verify = False
#     operating_system = "windows"
#     requests.packages.urllib3.disable_warnings()
# else:
#     verify = True
#     operating_system = "not windows"


class UploadClient(BaseHttpClient):
    def __init__(
        self,
        upload_url: str = "http://localhost:10800/v1/upload",
        headers: dict = {"X-Florence-Token": "X-Florence-Token"},
    ):
        super().__init__()
        # TODO Actual values for `upload_url` and `headers` (see `POST` request  in `upload_new()`)
        self.upload_url = upload_url
        self.headers = headers

    def upload_new(
        self, csv_path: str, is_publishable: bool = False, output_path: str = None
    ):
        """
        Upload files to the DP Upload Service. Files are chunked (default chunk size 5242880 bytes)
        """
        # Get size of file to be uploaded
        resumable_total_size = str(os.path.getsize(csv_path))

        # Get file name from file path
        resumable_file_name = csv_path.split("/")[-1]

        # Get teimstamp to create `path` value in `POST` params
        timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

        # Chunk file
        file_chunks = self._create_temp_chunks(
            csv_path=csv_path, output_path=output_path
        )

        resumable_chunk_number = 1

        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}
                # Construct `POST` request params for each file chunk
                params = {
                    "resumableFilename": resumable_file_name,
                    # TODO Check `path` value (replaces resumableIdentifier?).
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
                # Query string: ?resumableFilename=countries.csv&path=270224095333-countries-csv&isPublishable=False&collectionId=optional+for+upload%2C+required+before+publishing&title=title+value&resumableTotalSize=6198846&resumableType=text%2Fcsv&licence=licence+value&licenceUrl=licenceUrl+value&resumableChunkNumber=1&resumableTotalChunks=2

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
        self, csv_path: str, chunk_size: int = 5242880, output_path: str = None
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
