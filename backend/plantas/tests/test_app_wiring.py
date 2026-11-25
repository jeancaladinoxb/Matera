from unittest.mock import Mock

from backend import app as app_module


_ENVIRONMENT = {
    "DB_HOST": "db.test.invalid",
    "DB_PORT": "5432",
    "DB_NAME": "test_database",
    "DB_USER": "test_user",
    "DB_PASSWORD": "fake-password",
    "JWT_SECRET": "fake-secret-that-is-long-enough-for-hs256",
    "JWT_EXPIRATION_HOURS": "5",
    "CORS_ALLOWED_ORIGINS": "http://localhost:5173",
    "CLAIM_MASTER_KEY": "fake-claim-master-key-that-is-long-enough",
    "DEVICE_JWT_SECRET": "fake-device-secret-that-is-long-enough-1",
}


def test_create_app_registers_protected_plantas_routes(monkeypatch) -> None:
    for variable, value in _ENVIRONMENT.items():
        monkeypatch.setenv(variable, value)
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    client = app_module.create_app().test_client()

    assert client.get("/plantas").status_code == 401
    assert client.post("/materas/1/planta", json={"planta_id": 1}).status_code == 401
