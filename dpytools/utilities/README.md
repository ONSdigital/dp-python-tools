# Utility Functions

## str_to_bool

The `str_to_bool` function is a utility function that converts a string representation of a boolean to a boolean value.

### Usage

```python
from utilities import str_to_bool

print(str_to_bool('True'))  # Outputs: True
print(str_to_bool('false'))  # Outputs: False

```

#### Parameters
`should_be_bool` (str): A string that should represent a boolean value.

#### Returns
`bool`: The boolean value represented by the input string.

#### Raises
`AssertionError`: If the input value is not a string.
`ValueError`: If the input string does not represent a boolean value.

#### Example

```python
try:
    print(str_to_bool('not a boolean'))  # Raises ValueError
except ValueError as e:
    print(e)  # Outputs: A str value representing a boolean should be one of 'True', 'true', 'False', 'false'. Got 'not a boolean'
```
