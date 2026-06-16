from pydantic import BaseModel, Field

class DbHealthResponse(BaseModel):
    database: str = Field(..., description='Estado de la conexión a la base de datos', examples=['connected'])
