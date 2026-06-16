from pydantic import BaseModel, Field

class DynamicsHealthResponse(BaseModel):
    dynamics: str = Field(..., description='Estado de la conexión OData con Dynamics 365', examples=['connected'])
