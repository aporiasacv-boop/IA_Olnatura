from app.services.password_service import PasswordService

def test_hash_and_verify_password() -> None:
    service = PasswordService()
    password_hash = service.hash_password('Admin123!')
    assert password_hash != 'Admin123!'
    assert service.verify_password('Admin123!', password_hash) is True
    assert service.verify_password('wrong', password_hash) is False
