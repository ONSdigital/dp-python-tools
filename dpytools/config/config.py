from __future__ import annotations

import os
from typing import Any, Dict, List

from dpytools.config.properties.base import BaseProperty
from dpytools.config.properties.intproperty import IntegerProperty
from dpytools.config.properties.string import StringProperty


class Config:

    def __init__(self):
        self._properties_to_validate: List[BaseProperty] = []

    @staticmethod
    def from_env(config_dict: Dict[str, Dict[str, Any]]) -> Config:

        config = Config()

        for env_var_name, value in config_dict.items():

            value_for_property = os.environ.get(env_var_name, None)
            assert (
                value_for_property is not None
            ), f'Required environment value "{env_var_name}" could not be found.'

            if value["class"] == StringProperty:
                if value["kwargs"]:
                    regex = value["kwargs"].get("regex")
                    min_len = value["kwargs"].get("min_len")
                    max_len = value["kwargs"].get("max_len")
                else:
                    regex = None
                    min_len = None
                    max_len = None

                stringprop = StringProperty(
                    _name=value["property"],
                    _value=value_for_property,
                    regex=regex,
                    min_len=min_len,
                    max_len=max_len,
                )

                prop_name = value["property"]
                setattr(config, prop_name, stringprop)
                config._properties_to_validate.append(stringprop)

            elif value["class"] == IntegerProperty:
                if value["kwargs"]:
                    min_val = value["kwargs"].get("min_val")
                    max_val = value["kwargs"].get("max_val")
                else:
                    min_val = None
                    max_val = None

                intprop = IntegerProperty(
                    _name=value["property"],
                    _value=value_for_property,
                    min_val=min_val,
                    max_val=max_val,
                )

                prop_name = value["property"]
                setattr(config, prop_name, intprop)
                config._properties_to_validate.append(intprop)

            else:
                prop_type = value["class"]
                raise TypeError(
                    f"Unsupported property type specified via 'property' field, got {prop_type}. Should be of type StringProperty or IntegerProperty"
                )

        return config

    def assert_valid_config(self):
        """
        Assert that then Config class has the properties that
        provided properties.
        """
        for property in self._properties_to_validate:
            property.type_is_valid()
            property.secondary_validation()

        self._properties_to_validate = []
