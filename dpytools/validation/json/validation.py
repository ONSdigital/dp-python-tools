import json
from pathlib import Path
from typing import Dict, Optional, Union
from urllib.parse import urlparse

import jsonschema
from jsonschema import ValidationError


def validate_json_schema(
    schema_path: Union[Path, str],
    data_dict: Optional[Dict] = None,
    data_path: Optional[Union[Path, str]] = None,
    error_msg: Optional[str] = None,
    indent: Optional[int] = None,
):
    """
    Validate a JSON file against a schema.

    Either `data_dict` or `data_path` must be provided.

    `error_msg` and `indent` can be used to format the error message if validation fails.
    """
    # Confirm that *either* `data_dict` *or* `data_path` has been provided, otherwise raise ValueError
    if data_dict and data_path:
        raise ValueError(
            "Both a dictionary and file path of data have been provided - please specify either one or the other, not both."
        )
    if data_dict is None and data_path is None:
        raise ValueError(
            "Please provide either a dictionary or a file path of the data to be validated against the schema."
        )

    # Load schema as dict
    if isinstance(schema_path, str):
        parsed_schema_path = urlparse(schema_path)
        if parsed_schema_path.scheme == "http":
            # TODO Load schema from URL
            raise NotImplementedError("Validation from remote schema not yet supported")
        # Convert `schema_path` to pathlib.Path
        schema_path = Path(schema_path).absolute()
    # Check `schema_path` exists
    if not schema_path.exists():
        raise ValueError(f"Schema path '{schema_path}' does not exist")
    with open(schema_path, "r") as f:
        schema_from_path = json.load(f)

    # Load data to be validated
    if data_dict:
        if not isinstance(data_dict, Dict):
            raise ValueError(
                "Invalid data format, `data_dict` should be a Python dictionary"
            )
        data_to_validate = data_dict

    if data_path:
        # Convert `data_path` to pathlib.Path
        if isinstance(data_path, str):
            data_path = Path(data_path).absolute()
        if not isinstance(data_path, Path):
            raise ValueError(
                "Invalid data format, `data_path` should be a pathlib.Path or string of file location"
            )
        # Check `data_path` exists
        if not data_path.exists():
            raise ValueError(f"Data path '{data_path}' does not exist")
        with open(data_path, "r") as f:
            data_to_validate = json.load(f)

    # Validate data against schema
    try:
        jsonschema.validate(data_to_validate, schema_from_path)
    # TODO Handle jsonschema.SchemaError?
    except jsonschema.ValidationError as err:
        # If error is in a specific field, get the JSON path of the error location
        if err.json_path != "$":
            error_location = err.json_path
        else:
            error_location = "JSON data"
        # Create formatted message to be output on ValidationError
        if error_msg or indent:
            formatted_msg = f"""
Exception: {error_msg}
Exception details: {err.message}
Exception location: {error_location}
JSON data:
{json.dumps(data_to_validate, indent=indent)}
"""
            print(formatted_msg)
            raise ValidationError(formatted_msg) from err
        raise err
