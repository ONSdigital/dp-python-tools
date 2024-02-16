# dpytools: Config

Configuration class to enforce and police python application settings.

## Usage

The from_env() method is used to define a config object and populate it with 
a dictionary as input. The attributes of the created Config object are generated 
from the contents of the dictionary. See below example.

## Basic Example

Say we want to instantiate a config object, setting our configuration with an environment variable.
The environment variable will be called `MY_SERVER_ENDPOINT` and we want its value to be a URL.

```python
# The environment variable we want to use for our config. The value is a string of a URL.
MY_SERVER_ENDPOINT = "http://my-url.com"
```

When using the from_env() method to instantiate the config, we want to look up the  environment 
variable's value and to also make sure that value is a string that looks like a URL, so let's say
it should begin with "http://".

The code below shows how this instantiation would work using the from_env() method.

```python
from dpytools import Config
from dpytools.config.properties import StringProperty, IntegerProperty

config = Config.from_env({
    "MY_SERVER_ENDPOINT": {
        "class": StringProperty,
        "property", "server"
        "kwargs": {
            "regex": "http://.*"
        },
    }
    })

```

After it is instantiated, we can access the config's values using its class attributes with this notation: 

config.server.value

Where "config" is the name of the config object, "server" is the property name taken from the environment 
variable, and "value" represents the URL value of the "server" property.

```python
print(config.server.value)
```

Would return http://myurl.com

## Properties

When providing the input dictionary for instantiating the config, you can specify different property types 
that determine what they represent, how they can be configured, how they are validated.

### StringProperty

This type of property ensures configuration values are non-blank strings, while providing some optional 
configuration to be done on the value, such as regex to check for matching strings, and setting a 
minimum length and a maximum length.

An example of a config with a StringProperty being instantiated, also using all the optional configuration:

```python
SOME_STRING_ENV_VAR = "Test string"

config = Config.from_env({
    "SOME_STRING_ENV_VAR": {
        "class": StringProperty,
        "property": "mystring",
        "kwargs": {
            "regex": "Test",
            "min_len": 10
            "max_len": 100
        },
    }
})

# config.mystring.value would be "Test string"
```

### IntegerProperty

This type of property ensures configuration values are an integer, or an object that can be cast to int.
The optional configuration that can be used with IntegerProperty allows restrictions on the minimum 
or maximum values of the integer.

An example of a config with an IntegerProperty being instantiated, using the minimum and maximmum value
options:

```python
SOME_INT_ENV_VAR = 8

config = Config.from_env({
    "SOME_INT_ENV_VAR": {
        "class": IntegerProperty,
        "property": "myinteger"
        "kwargs": {
            "min_value": 1,
            "max_value": 10
        }
    }
})

# config.myinteger.value would be 8
```

## Larger example
Instantiation of a config can use multiple properties of varying types by including them in 
the input dictionary, their values will all be taken from env variables if they correspond 
correctly. An example with a more detailed configuration being created is shown below.

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
but they are generated dynamically. Accessing the value for the first property, name1, would be 
done like so:

```python
foo = config.name1.value
```
