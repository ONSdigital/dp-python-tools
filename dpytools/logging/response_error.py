from pydantic import BaseModel


class DatasetResponseError(BaseModel):
    cause: str
    error_code: str
    description: str
