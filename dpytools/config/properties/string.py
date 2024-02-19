from typing import Optional
from dataclasses import dataclass
from .base import BaseProperty

import re

@dataclass
class StringProperty(BaseProperty):
    regex: Optional[str]
    min_len: Optional[int]
    max_len: Optional[int]

    def type_is_valid(self):
        """
        Validate that the property looks like
        its of the correct type 
        """
        try:
            str(self._value)
        except Exception as err:
            raise Exception(f"Cannot cast {self.name} value {self._value} to string.") from err

    def secondary_validation(self):
        """
        Non type based validation you might want to
        run against a configuration value of this kind.
        """
        
        if len(self._value) == 0:
            raise ValueError(f"Str value for {self.name} is an empty string")
        
        if self.regex:
            # TODO - confirm the value matches the regex
            regex_search = re.search(self.regex, self._value)
            if not regex_search:
                raise ValueError(f"Str value for {self.name} does not match the given regex.")

        if self.min_len:
            if len(self._value) < self.min_len:
                raise ValueError(f"Str value for {self.name} is shorter than minimum length {self.min_len}")

        if self.max_len:
            if len(self._value) > self.max_len:
                raise ValueError(f"Str value for {self.name} is longer than maximum length {self.max_len}")