from typing import Optional
from dataclasses import dataclass
from .base import BaseProperty

@dataclass
class IntegerProperty(BaseProperty):
    min_val: Optional[int]
    max_val: Optional[int]

    def type_is_valid(self):
        """
        Validate that the property looks like
        its of the correct type 
        """
        try:
            int(self._value)
        except Exception as err:
            raise Exception(f"Cannot cast {self._name} value {self._value} to integer.") from err

    def secondary_validation(self):
        """
        Non type based validation you might want to
        run against a configuration value of this kind.
        """
        if not self._value:
            raise ValueError(f"Integer value for {self._name} does not exist.")

        if self.min_val and self._value < self.min_val:
            raise ValueError(f"Integer value for {self._name} is lower than allowed minimum.")

        if self.max_val and self._value > self.max_val:
            raise ValueError(f"Integer value for {self._name} is higher than allowed maximum.")