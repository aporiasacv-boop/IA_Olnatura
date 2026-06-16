from pydantic import BaseModel, Field

class RootResponse(BaseModel):
    message: str = Field(..., description='Mensaje de bienvenida')
    app_name: str = Field(..., description='Nombre de la aplicación')
    version: str = Field(..., description='Versión desplegada')
    docs_url: str = Field(..., description='Ruta a la documentación interactiva')
