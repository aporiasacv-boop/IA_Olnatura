class RAGError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class UnsupportedDocumentError(RAGError):
    pass

class DocumentLoadError(RAGError):
    pass
