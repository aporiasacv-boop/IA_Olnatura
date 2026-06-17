from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class LoginResponse(BaseModel):
    username: str
    role: str

class LogoutResponse(BaseModel):
    message: str = 'Sesión cerrada correctamente'

class CurrentUserResponse(BaseModel):
    username: str
    role: str
