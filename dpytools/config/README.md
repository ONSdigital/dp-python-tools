# dpytools: Config

Configuration class to enforce and police python application settings.

## Usage

The from_env() method is used to define a config object and populate it with 
a dictionary as input. The attributes of the created Config object are generated 
from the contents of the dictionary. See below example.

Instantiation of a config from an input dictionary with values taken from env variables:

```python
from dpytools import Config
from dpytools.config.properties import StringProperty, IntegerProperty

config = Config.from_env({
    "SOME_STRING_ENV_VAR": {
        "class": StringProperty,
        "property": "name1",
        "kwargs": {
            "regex": "I match a thing",
            "min_len": 10
        },
    },
    "SOME_URL_ENV_VAR": {
        "class": StringProperty,
        "property", "name2"
        "kwargs": {
            "regex": "https://.*"
        },
    },
    "SOME_INT_ENV_VAR": {
        "class": IntegerProperty,
        "property": "name3"
        "kwargs": {
            "min_value": 5,
            "max_value": 27
        }
    },
})

# Note: Validation checks are separate from instantiation to allow some nuance, 
# but you'd likely not want to start an app with invalid configuration.
config.assert_valid_config()
```

The attributes of the config object can be accessed like you would expect from a class' attributes,
but they are generated dynamically:

```python
foo = config.name1.value
```
