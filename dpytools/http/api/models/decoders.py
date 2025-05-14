from enum import Enum
from json import JSONDecoder


class EnumDecoder(JSONDecoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
