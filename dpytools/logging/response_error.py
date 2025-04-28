from typing import Dict
from pydantic import BaseModel


class DatasetResponseError(BaseModel):
    cause: str
    error_code: str
    description: str


def map_error_json_to_object(error_dict: Dict):
    # Check if the input contains all the fields expected in an error response.
    if "Cause" and "Code" and "Description" in error_dict:
        cause = error_dict["Cause"]
        error_code = error_dict["Code"]
        description = error_dict["Description"]

        response_error = DatasetResponseError(
            cause=cause, error_code=error_code, description=description
        )
        return response_error

    else:
        # If the error from the response is not formatted according to expected standards, then raise this error instead
        raise ValueError(
            f"Error dict does not contain expected error keys (Cause, Code, Description). Dictionary contents: {error_dict}"
        )
