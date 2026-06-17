from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from app.core.config import settings

_PUBLIC_UI_PATHS = frozenset({
    '/ui/login.html',
    '/ui/css/olnatura.css',
    '/ui/js/login.js',
})

class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.AUTH_ENABLED:
            return await call_next(request)
        path = request.url.path
        if not self._is_protected(path):
            return await call_next(request)
        if path in _PUBLIC_UI_PATHS:
            return await call_next(request)
        user_id = request.session.get('user_id')
        if user_id:
            return await call_next(request)
        if path.startswith('/assistant'):
            return JSONResponse(status_code=401, content={'detail': 'No autenticado'})
        return RedirectResponse(url='/ui/login.html', status_code=303)

    @staticmethod
    def _is_protected(path: str) -> bool:
        return path.startswith('/assistant') or path.startswith('/ui')
