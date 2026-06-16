from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., description='Estado del servicio', examples=['ok'])
    app_name: str = Field(..., description='Nombre de la aplicación')
    version: str = Field(..., description='Versión desplegada')
