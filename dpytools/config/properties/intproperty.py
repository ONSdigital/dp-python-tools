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
            raise Exception(f"Cannot cast {self.name} value {self.value} to integer.") from err

    def secondary_validation(self):
        """
        Non type based validation you might want to
        run against a configuration value of this kind.
        """
        if not self.value:
            raise ValueError(f"Integer value for {self.name} does not exist.")

        if self.min_val and int(self.value) < self.min_val:
            raise ValueError(f"Integer value for {self.name} is lower than allowed minimum.")

        if self.max_val and int(self.value) > self.max_val:
            raise ValueError(f"Integer value for {self.name} is higher than allowed maximum.")