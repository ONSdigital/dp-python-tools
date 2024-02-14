from pathlib import Path
from jsonschema import ValidationError

import pytest
from dpytools.validation.json.validation import validate_json_schema


def test_validate_json_schema_data_path():
    """
    Validate data (as file path) against schema
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = "tests/test_cases/pipeline_config.json"
    assert (
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_path=pipeline_config,
        )
        is None
    )


def test_validate_json_schema_data_dict():
    """
    Validate data (as dictionary) against schema
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = {
        "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
        "required_files": [{"matches": "*.sdmx", "count": 1}],
        "supplementary_distributions": [{"matches": "*.sdmx", "count": 1}],
        "priority": 1,
        "contact": ["jobloggs@ons.gov.uk"],
        "pipeline": "default",
    }
    assert (
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_dict=pipeline_config,
        )
        is None
    )


def test_validate_json_schema_data_dict_and_data_path():
    """
    Raise ValueError if both `data_dict` and `data_path` are provided
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config_path = "tests/test_cases/pipeline_config.json"
    pipeline_config_dict = {
        "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
        "required_files": [{"matches": "*.sdmx", "count": 1}],
        "supplementary_distributions": [{"matches": "*.sdmx", "count": 1}],
        "priority": 1,
        "contact": ["jobloggs@ons.gov.uk"],
        "pipeline": "default",
    }
    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_dict=pipeline_config_dict,
            data_path=pipeline_config_path,
        )
    assert (
        "Both a dictionary and file path of data have been provided - please specify either one or the other, not both."
        in str(err.value)
    )


def test_validate_json_schema_no_data_dict_or_data_path():
    """
    Raise ValueError if neither `data_dict` or `data_path` are provided
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"

    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
        )
    assert (
        "Please provide either a dictionary or a file path of the data to be validated against the schema."
        in str(err.value)
    )


def test_validate_json_schema_invalid_data_path_format():
    """
    Raise ValueError if data_path is not a string or file path
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = ["Invalid", "data", "format"]
    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema, data_path=pipeline_config
        )
    assert (
        "Invalid data format, `data_path` should be a pathlib.Path or string of file location"
        in str(err.value)
    )


def test_validate_json_schema_invalid_data_dict_format():
    """
    Raise ValueError if data_dict is not a dictionary
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = ["Invalid", "data", "format"]
    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema, data_dict=pipeline_config
        )
    assert "Invalid data format, `data_dict` should be a Python dictionary" in str(
        err.value
    )


def test_validate_json_schema_url():
    """
    Raise NotImplementedError if `schema_path` is a URL (i.e. not a local file)
    """
    pipeline_config_schema = "http://example.org"
    pipeline_config = "tests/test_cases/pipeline_config.json"
    with pytest.raises(NotImplementedError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema, data_path=pipeline_config
        )
    assert "Validation from remote schema not yet supported" in str(err.value)


def test_validate_json_schema_invalid_schema_path():
    """
    Raise ValueError if `schema_path` does not exist
    """
    pipeline_config_schema = "tests/test_cases/does_not_exist.json"
    pipeline_config = "tests/test_cases/pipeline_config.json"
    schema_path = Path(pipeline_config_schema).absolute()
    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema, data_path=pipeline_config
        )
    assert f"Schema path '{schema_path}' does not exist" in str(err.value)


def test_validate_json_schema_invalid_data_path():
    """
    Raise ValueError if `data_path` does not exist
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = "tests/test_cases/does_not_exist.json"
    data_path = Path(pipeline_config).absolute()
    with pytest.raises(ValueError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema, data_path=pipeline_config
        )
    assert f"Data path '{data_path}' does not exist" in str(err.value)


def test_validate_json_schema_data_path_required_field_missing():
    """
    Raises ValidationError due to missing field in `data_path` JSON
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = "tests/test_cases/pipeline_config_missing_required_field.json"
    with pytest.raises(ValidationError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_path=pipeline_config,
            # error_msg="Error validating pipeline_config_missing_required_field.json",
            # indent=2,
        )
    assert "'priority' is a required property" in str(err.value)


def test_validate_json_schema_data_path_invalid_data_type():
    """
    Raises ValidationError due to invalid data type in `data_path` JSON
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = "tests/test_cases/pipeline_config_invalid_data_type.json"
    with pytest.raises(ValidationError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_path=pipeline_config,
            error_msg="Error validating pipeline_config_invalid_data_type.json",
        )
    assert "'1' is not of type 'integer'" in str(err.value)


def test_validate_json_schema_data_dict_required_field_missing():
    """
    Raises ValidationError due to missing field in `data_dict`
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = {
        "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
        "required_files": [{"matches": "*.sdmx", "count": 1}],
        "supplementary_distributions": [{"matches": "*.sdmx", "count": 1}],
        "contact": ["jobloggs@ons.gov.uk"],
        "pipeline": "default",
    }
    with pytest.raises(ValidationError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_dict=pipeline_config,
            error_msg="Error validating pipeline_config with required field missing",
        )
    assert "'priority' is a required property" in str(err.value)


def test_validate_json_schema_data_dict_invalid_data_type():
    """
    Raises ValidationError due to invalid data type in `data_dict`
    """
    pipeline_config_schema = "tests/test_cases/pipeline_config_schema.json"
    pipeline_config = {
        "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
        "required_files": [{"matches": "*.sdmx", "count": 1}],
        "supplementary_distributions": [{"matches": "*.sdmx", "count": "1"}],
        "priority": 1,
        "contact": ["jobloggs@ons.gov.uk"],
        "pipeline": "default",
    }
    with pytest.raises(ValidationError) as err:
        validate_json_schema(
            schema_path=pipeline_config_schema,
            data_dict=pipeline_config,
            error_msg="Error validating pipeline_config dict with invalid data type",
        )
    assert "'1' is not of type 'integer'" in str(err.value)
