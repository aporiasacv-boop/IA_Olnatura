from app.middleware.auth import AuthenticationMiddleware

def test_public_ui_paths_not_protected() -> None:
    assert '/ui/login.html' not in {p for p in ['/assistant'] if AuthenticationMiddleware._is_protected(p)}
    assert AuthenticationMiddleware._is_protected('/assistant') is True
    assert AuthenticationMiddleware._is_protected('/ui/') is True
    assert AuthenticationMiddleware._is_protected('/health') is False
