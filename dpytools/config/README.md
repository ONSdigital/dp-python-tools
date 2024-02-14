# dpytools: Config

Configuration class to enforce and police python application settings.

## Usage

Getting configuration properties from env vars:

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

# Note: separate from instantiation to allow some nuance, but you'd likely
# not want to start an app with invalid config.
config.assert_valid_config()

# Accessed via
foo = config.name1.value
```

## What about default values?

For env var defaults use [a .env file](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1) which should be excluded from the build.

If a default _is_ intended for the build the consider whether its a constant rather than an env var.
