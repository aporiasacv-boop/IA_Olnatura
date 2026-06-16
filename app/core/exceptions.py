class AppException(Exception):

    def __init__(self, message: str, status_code: int=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(AppException):

    def __init__(self, message: str='Recurso no encontrado'):
        super().__init__(message=message, status_code=404)

class ValidationException(AppException):

    def __init__(self, message: str='Error de validación'):
        super().__init__(message=message, status_code=422)
