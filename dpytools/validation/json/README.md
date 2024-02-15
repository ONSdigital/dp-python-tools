# dpytools: Validation

Utility functions for validating a JSON file against a given JSON schema.

## Usage

### `validate_json_schema()`

The `validate_json_schema()` function allows you to validate JSON content against an appropriate JSON schema. The JSON content to be validated can either be a JSON file (either as a string or a `pathlib.Path`), or a Python dictionary. If both a JSON file and a Python dictionary are provided, this will raise an error - only one of these arguments should be specified.

The JSON schema should be a JSON file (either as a string or a `pathlib.Path`).

Two optional arguments, `error_msg` and `indent`, can be used to output validation errors to the console in a user-friendly format.

#### `data_path` example

```python
from dpytools.validation.json.validation import validate_json_schema

schema_path = "path/to/schema.json"
data_path = "path/to/data.json"

# Optional error_msg and indent arguments to print user-friendly output if validation fails
error_msg = f"Validating {data_path}"
indent = 2

validate_json_schema(
    schema_path=schema_path,
    data_path=data_path,
    error_msg=error_msg,
    indent=2
)
```

#### `data_dict` example

```python
from dpytools.validation.json.validation import validate_json_schema

schema_path = "path/to/schema.json"
data_dict = {
    "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
    "required_files": [
        {
            "matches": "*.sdmx",
            "count": 1
        }
    ],
    "supplementary_distributions": [
        {
            "matches": "*.sdmx",
            "count": 1
        }
    ],
    "priority": 1,
    "contact": ["jobloggs@ons.gov.uk"],
    "pipeline": "default",
}

# Optional error_msg and indent arguments to print user-friendly output if validation fails
error_msg = "Validating data_dict"
indent = 2

validate_json_schema(
    schema_path=schema_path,
    data_dict=data_dict,
    error_msg=error_msg,
    indent=2
)
```

#### Non-validation errors

If there are any problems with the inputs provided, such as invalid file locations or formats, this will raise an error with information on how to resolve the issue.

#### Validation errors

If the `data.json` file satisfies the requirements of `schema.json`, calling the `validate_json_schema()` function will return nothing.

If there are validation errors in `data.json`, and `error_msg` or `indent` arguments have been provided, details will be output to the console. For example, if `data.json` is missing a field that is `required` in `schema.json`, the output will resemble the following:

```
Exception: Validating path/to/data.json
Exception details: 'priority' is a required property
Exception location: JSON data
JSON data:
{
  "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
  "required_files": [
    {
      "matches": "*.sdmx",
      "count": 1
    }
  ],
  "supplementary_distributions": [
    {
      "matches": "*.sdmx",
      "count": 1
    }
  ],
  "contact": [
    "jobloggs@ons.gov.uk"
  ],
  "pipeline": "default"
}
```

If the validation error relates to a specific field in `data.json`, for example, the data type used for a value is incorrect, `Exception location` indicates the precise location of the error. In the example below, the `count` field in `required_files[0]` is a string, but should be an integer:

```
Exception: Validating path/to/data.json
Exception details: '1' is not of type 'integer'
Exception location: $.required_files[0].count
JSON data:
{
  "schema": "airflow.schemas.ingress.sdmx.v1.schema.json",
  "required_files": [
    {
      "matches": "*.sdmx",
      "count": "1"
    }
  ],
  "supplementary_distributions": [
    {
      "matches": "*.sdmx",
      "count": 1
    }
  ],
  "priority": 1,
  "contact": [
    "jobloggs@ons.gov.uk"
  ],
  "pipeline": "default"
}
```

Compare this to the unformatted output if `error_msg` and `indent` are not provided:

```
jsonschema.exceptions.ValidationError: '1' is not of type 'integer'

Failed validating 'type' in schema['properties']['required_files']['items'][0]['properties']['count']:
    {'type': 'integer'}

On instance['required_files'][0]['count']:
    '1'
```
