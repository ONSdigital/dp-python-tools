class DataException(Exception):
    def __init__(self, message: str, data: dict, *args):
        super().__init__(message, *args)
        self.data = data