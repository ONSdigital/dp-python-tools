from _pytest.monkeypatch import monkeypatch
import pytest

from dpytools.config.config import Config
from dpytools.config.properties.string import StringProperty
from dpytools.config.properties.intproperty import IntegerProperty

def test_config_loader(monkeypatch):
    """
    Tests that a config object can be created and its attributes 
    dynamically generated from an input config dictionary with the 
    expected contents.
    """

    # Assigning environment variable values for config dictionary values
    monkeypatch.setenv("SOME_STRING_ENV_VAR", "Some string value")
    monkeypatch.setenv("SOME_URL_ENV_VAR", "https://test.com/some-url")
    monkeypatch.setenv("SOME_INT_ENV_VAR", "6")

    config_dictionary = {
    "SOME_STRING_ENV_VAR": {
        "class": StringProperty,
        "property": "name1",
        "kwargs": {
            "regex": "string value",
            "min_len": 10
        },
    },
    "SOME_URL_ENV_VAR": {
        "class": StringProperty,
        "property": "name2",
        "kwargs": {
            "regex": "https://.*",
            "max_len": 100
        },
    },
    "SOME_INT_ENV_VAR": {
        "class": IntegerProperty,
        "property": "name3",
        "kwargs": {
            "min_val": 5,
            "max_val": 27
        }
    },
}

    config = Config.from_env(config_dictionary)
    
    # Assertions

    assert config.name1.name == "name1"
    assert config.name1.value == "Some string value"
    assert config.name1.min_len == 10
    assert config.name1.regex == "string value"

    assert config.name2.name == "name2"
    assert config.name2.value == "https://test.com/some-url"
    assert config.name2.regex == "https://.*"
    assert config.name2.max_len == 100

    assert config.name3.name == "name3"
    assert config.name3.min_val == 5
    assert config.name3.max_val == 27


def test_config_loader_no_values_error():
    """
    Tests that an exception will be raised when a config object 
    is created using the from_env() method but the environment 
    variable values have not been assigned (values are None).
    """

    # No environment variable values assigned in this test

    config_dictionary = {
    "SOME_STRING_ENV_VAR": {
        "class": StringProperty,
        "property": "name1",
        "kwargs": {
            "min_len": 10
        },
    }
}

    with pytest.raises(Exception) as e:

        config = Config.from_env(config_dictionary)

    assert 'Required environment value "SOME_STRING_ENV_VAR" could not be found.' in str(e.value)


def test_config_loader_incorrect_type_error(monkeypatch):
    """
    Tests that a TypeError will be raised when a config object 
    is created using the from_env() method but the type of an
    attribute being created is not either a StringProperty or IntegerProperty.
    """

    monkeypatch.setenv("SOME_STRING_ENV_VAR", "Some string value")

    config_dictionary = {
    "SOME_STRING_ENV_VAR": {
        "class": int,
        "property": "name1",
        "kwargs": {
            "min_val": 10,

        },
    }
}

    with pytest.raises(TypeError) as e:

        config = Config.from_env(config_dictionary)

    assert "Unsupported property type specified via 'property' field, got <class 'int'>. Should be of type StringProperty or IntegerProperty" in str(e.value)