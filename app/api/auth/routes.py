from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import RedirectResponse
from app.api.deps import get_auth_service, get_current_user
from app.core.logging import get_logger
from app.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse, LogoutResponse
from app.services.auth_service import AuthService, AuthenticatedUser

router = APIRouter()
logger = get_logger(__name__)

@router.post('/login', response_model=LoginResponse, summary='Iniciar sesión', tags=['Auth'])
def login(request: Request, body: LoginRequest, auth_service: AuthService=Depends(get_auth_service)) -> LoginResponse:
    user = auth_service.authenticate(body.username, body.password)
    if user is None:
        logger.warning('Intento de login fallido para usuario=%s', body.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciales inválidas')
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    request.session['role'] = user.role.value
    logger.info('Login exitoso usuario=%s role=%s', user.username, user.role.value)
    return LoginResponse(username=user.username, role=user.role.value)

@router.post('/logout', response_model=LogoutResponse, summary='Cerrar sesión', tags=['Auth'])
def logout(request: Request) -> LogoutResponse:
    username = request.session.get('username', 'desconocido')
    request.session.clear()
    logger.info('Logout usuario=%s', username)
    return LogoutResponse()

@router.get('/logout', summary='Cerrar sesión y redirigir al login', tags=['Auth'])
def logout_redirect(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url='/ui/login.html', status_code=303)

@router.get('/me', response_model=CurrentUserResponse, summary='Usuario autenticado actual', tags=['Auth'])
def current_user(user: AuthenticatedUser=Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(username=user.username, role=user.role.value)
