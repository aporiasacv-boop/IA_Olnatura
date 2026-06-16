class DocumentLoaderError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class DocumentNotFoundError(DocumentLoaderError):
    pass

class UnsupportedDocumentFormatError(DocumentLoaderError):
    pass

class DocumentTextExtractionError(DocumentLoaderError):
    pass
