import os
import tempfile
import uuid

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["ENVIRONMENT"] = "development"
os.environ["TESTING"] = "true"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:3000"]'

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base, get_db
from backend.app.main import app

TEST_DB = f"sqlite:///{tempfile.mktemp(suffix='.db')}"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

TEST_PASSWORD = "Secure1234"
TEST_NAME = "Test User"


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def _register(email=None, password=TEST_PASSWORD, full_name=TEST_NAME):
    if email is None:
        email = _unique_email()
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
    })
    return res, email


def _login(email, password=TEST_PASSWORD):
    return client.post("/auth/login", data={
        "username": email,
        "password": password,
    })


def _get_verification_token(email):
    from backend.app.models.user import User
    db = TestSession()
    user = db.query(User).filter(User.email == email).first()
    token = user.verification_token
    db.close()
    return token


def _verify_user(email):
    token = _get_verification_token(email)
    return client.post(f"/auth/verify-email?token={token}")


def _register_and_verify(password=TEST_PASSWORD):
    res, email = _register(password=password)
    assert res.status_code == 200
    _verify_user(email)
    return email


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestRegistration:
    def test_register_success(self):
        res, email = _register()
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == email
        assert data["full_name"] == TEST_NAME

    def test_register_duplicate_email(self):
        _, email = _register()
        res = client.post("/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME,
        })
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]

    def test_register_weak_password_too_short(self):
        res, _ = _register(password="Ab1")
        assert res.status_code == 422

    def test_register_weak_password_no_uppercase(self):
        res, _ = _register(password="secure1234")
        assert res.status_code == 422

    def test_register_weak_password_no_digit(self):
        res, _ = _register(password="SecurePass")
        assert res.status_code == 422


class TestEmailVerification:
    def test_login_blocked_without_verification(self):
        _, email = _register()
        res = _login(email)
        assert res.status_code == 403
        assert "not verified" in res.json()["detail"]

    def test_verify_email_success(self):
        _, email = _register()
        res = _verify_user(email)
        assert res.status_code == 200
        assert "verified" in res.json()["detail"].lower()

    def test_verify_invalid_token(self):
        res = client.post("/auth/verify-email?token=invalid-token")
        assert res.status_code == 400

    def test_login_after_verification(self):
        email = _register_and_verify()
        res = _login(email)
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_resend_verification(self):
        _, email = _register()
        res = client.post("/auth/resend-verification", json={"email": email})
        assert res.status_code == 200

    def test_resend_verification_unknown_email(self):
        res = client.post("/auth/resend-verification", json={"email": "nobody@example.com"})
        assert res.status_code == 200


class TestLogin:
    def test_login_wrong_password(self):
        email = _register_and_verify()
        res = _login(email, password="WrongPass1")
        assert res.status_code == 401

    def test_login_nonexistent_user(self):
        res = _login("nobody@example.com")
        assert res.status_code == 401

    def test_login_sets_cookie(self):
        email = _register_and_verify()
        res = _login(email)
        assert res.status_code == 200
        assert "access_token" in res.cookies

    def test_logout_clears_cookie(self):
        email = _register_and_verify()
        _login(email)
        res = client.post("/auth/logout")
        assert res.status_code == 200


class TestAccountLockout:
    def test_lockout_after_failed_attempts(self):
        email = _register_and_verify()
        for _ in range(5):
            _login(email, password="WrongPass1")
        res = _login(email, password="WrongPass1")
        assert res.status_code == 423
        assert "locked" in res.json()["detail"].lower()

    def test_lockout_blocks_correct_password(self):
        email = _register_and_verify()
        for _ in range(5):
            _login(email, password="WrongPass1")
        res = _login(email)
        assert res.status_code == 423

    def test_successful_login_resets_counter(self):
        email = _register_and_verify()
        for _ in range(3):
            _login(email, password="WrongPass1")
        res = _login(email)
        assert res.status_code == 200
        for _ in range(3):
            _login(email, password="WrongPass1")
        res = _login(email)
        assert res.status_code == 200


class TestPasswordReset:
    def test_forgot_password_existing_email(self):
        _, email = _register()
        res = client.post("/auth/forgot-password", json={"email": email})
        assert res.status_code == 200
        assert "reset link" in res.json()["detail"].lower()

    def test_forgot_password_unknown_email(self):
        res = client.post("/auth/forgot-password", json={"email": "nobody@example.com"})
        assert res.status_code == 200

    def test_reset_password_success(self):
        email = _register_and_verify()
        from backend.app.core.security import create_scoped_token
        token = create_scoped_token(email, scope="password_reset", expires_minutes=30)
        new_password = "NewSecure1"
        res = client.post("/auth/reset-password", json={
            "token": token,
            "new_password": new_password,
        })
        assert res.status_code == 200
        res = _login(email, password=new_password)
        assert res.status_code == 200

    def test_reset_password_invalid_token(self):
        res = client.post("/auth/reset-password", json={
            "token": "invalid",
            "new_password": "NewSecure1",
        })
        assert res.status_code == 400

    def test_reset_password_weak_password(self):
        _, email = _register()
        from backend.app.core.security import create_scoped_token
        token = create_scoped_token(email, scope="password_reset", expires_minutes=30)
        res = client.post("/auth/reset-password", json={
            "token": token,
            "new_password": "weak",
        })
        assert res.status_code == 400

    def test_reset_clears_lockout(self):
        email = _register_and_verify()
        for _ in range(5):
            _login(email, password="WrongPass1")
        res = _login(email)
        assert res.status_code == 423

        from backend.app.core.security import create_scoped_token
        token = create_scoped_token(email, scope="password_reset", expires_minutes=30)
        client.post("/auth/reset-password", json={
            "token": token,
            "new_password": "NewSecure1",
        })
        res = _login(email, password="NewSecure1")
        assert res.status_code == 200


class TestProtectedEndpoints:
    def test_unauthenticated_access(self):
        res = client.get("/evolution/history")
        assert res.status_code == 401

    def test_authenticated_access(self):
        email = _register_and_verify()
        login_res = _login(email)
        token = login_res.json()["access_token"]
        res = client.get("/evolution/history", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


class TestAuditLog:
    def test_register_creates_audit_entry(self):
        _, email = _register()
        from backend.app.models.audit_log import AuditLog
        db = TestSession()
        entries = db.query(AuditLog).filter(AuditLog.action == "register").all()
        assert len(entries) >= 1
        db.close()

    def test_login_creates_audit_entries(self):
        email = _register_and_verify()
        _login(email)
        from backend.app.models.audit_log import AuditLog
        db = TestSession()
        success = db.query(AuditLog).filter(AuditLog.action == "login_success").all()
        assert len(success) >= 1
        db.close()

    def test_failed_login_creates_audit_entry(self):
        email = _register_and_verify()
        _login(email, password="WrongPass1")
        from backend.app.models.audit_log import AuditLog
        db = TestSession()
        failures = db.query(AuditLog).filter(AuditLog.action == "login_failed").all()
        assert len(failures) >= 1
        db.close()
