class DynamicsError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DynamicsAuthError(DynamicsError):
    pass

class DynamicsConnectionError(DynamicsError):
    pass

class DynamicsODataError(DynamicsError):

    def __init__(self, message: str, status_code: int | None=None):
        self.status_code = status_code
        super().__init__(message)
