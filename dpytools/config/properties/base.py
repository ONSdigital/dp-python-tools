from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Union, Tuple, Optional

@dataclass
class BaseProperty(metaclass=ABCMeta):
    _name: str
    _value: Any

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
         raise ValueError(f"Trying to change name property to value {value} but you cannot change a property name after instantiation.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        raise ValueError(f"Trying to change value to {value} but you cannot change a property value after instantiation.")

    @abstractmethod
    def type_is_valid(self):
        """
        Validate that the property looks like
        its of the correct type 
        """
        ...

    # Note: Won't apply to all types so its not
    # an abstract method, its just a normal method
    # we can overwrite where relevant.
    def secondary_validation(self):
        """
        Non type based validation you might want to
        run against a configuration value.
        """
        ...