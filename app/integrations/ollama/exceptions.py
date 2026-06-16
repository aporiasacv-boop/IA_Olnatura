class OllamaError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class OllamaConnectionError(OllamaError):
    pass

class OllamaAPIError(OllamaError):

    def __init__(self, message: str, status_code: int | None=None):
        self.status_code = status_code
        super().__init__(message)
