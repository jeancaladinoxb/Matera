from pathlib import Path
from unittest.mock import Mock

import pytest

from backend import app as app_module
from backend.usuarios.infrastructure.adapters.postgresql_repository_adapter import (
    connection_factory_from_environment,
)


_ENVIRONMENT = {
    "DB_HOST": "db.test.invalid",
    "DB_PORT": "5432",
    "DB_NAME": "test_database",
    "DB_USER": "test_user",
    "DB_PASSWORD": "fake-password",
    "JWT_SECRET": "fake-secret-that-is-long-enough-for-hs256",
    "JWT_EXPIRATION_HOURS": "5",
    "CORS_ALLOWED_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
    "CLAIM_MASTER_KEY": "fake-claim-master-key-that-is-long-enough",
    "DEVICE_JWT_SECRET": "fake-device-secret-that-is-long-enough-1",
}


def _set_fake_environment(monkeypatch) -> None:
    for variable, value in _ENVIRONMENT.items():
        monkeypatch.setenv(variable, value)


def test_create_app_loads_backend_env_and_registers_endpoints(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    load_dotenv = Mock(return_value=True)
    monkeypatch.setattr(app_module, "load_dotenv", load_dotenv)

    app = app_module.create_app()

    load_dotenv.assert_called_once_with(Path(app_module.__file__).resolve().parent / ".env")
    assert app.test_client().post("/registro").status_code == 400
    assert app.test_client().post("/login").status_code == 400
    assert app.test_client().post("/session/refresh").status_code == 401
    assert app.test_client().post("/logout").status_code == 204
    assert app.test_client().post("/materas/vincular").status_code == 401
    assert app.test_client().post("/dispositivos/activar").status_code == 400


def test_preflight_allows_credentials_only_for_configured_origins(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.setattr(app_module, "load_dotenv", Mock())
    client = app_module.create_app().test_client()

    allowed = client.options(
        "/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    rejected = client.options(
        "/login",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 204
    assert allowed.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert allowed.headers["Access-Control-Allow-Credentials"] == "true"
    assert allowed.headers["Vary"] == "Origin"
    assert "Access-Control-Allow-Origin" not in rejected.headers


def test_cookie_defaults_are_secure_in_production(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SAMESITE", raising=False)

    settings = app_module._session_cookie_settings(Mock(expiration_seconds=18_000))

    assert settings.name == "cuida_mate_session"
    assert settings.max_age_seconds == 18_000
    assert settings.secure is True
    assert settings.same_site == "Lax"


def test_none_same_site_requires_secure_cookie(monkeypatch) -> None:
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("SESSION_COOKIE_SAMESITE", "None")

    with pytest.raises(ValueError, match="SESSION_COOKIE_SECURE"):
        app_module._session_cookie_settings(Mock(expiration_seconds=18_000))


def test_create_app_fails_with_names_of_missing_database_variables(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.delenv("DB_USER")
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    with pytest.raises(RuntimeError, match="DB_USER"):
        app_module.create_app()


def test_create_app_fails_with_name_of_missing_jwt_variable(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.delenv("JWT_EXPIRATION_HOURS")
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    with pytest.raises(ValueError, match="JWT_EXPIRATION_HOURS"):
        app_module.create_app()


def test_database_factory_uses_only_fake_environment_values(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    connect = Mock(return_value=object())
    monkeypatch.setattr(
        "backend.usuarios.infrastructure.adapters.postgresql_repository_adapter.psycopg2.connect",
        connect,
    )

    connection_factory_from_environment()()

    connect.assert_called_once_with(
        host="db.test.invalid",
        port="5432",
        dbname="test_database",
        user="test_user",
        password="fake-password",
    )


def test_dotenv_file_is_never_loaded_by_tests(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    observed_paths = []

    def fake_load_dotenv(path):
        observed_paths.append(path)
        return True

    monkeypatch.setattr(app_module, "load_dotenv", fake_load_dotenv)
    app_module.create_app()

    assert observed_paths == [Path(app_module.__file__).resolve().parent / ".env"]


@pytest.mark.parametrize(
    "environment",
    (
        {"FLASK_DEBUG": "1"},
        {"FLASK_DEBUG": "true"},
        {"APP_ENV": "development"},
    ),
)
def test_development_test_page_is_registered_only_in_development(
    monkeypatch, environment
) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    for variable, value in environment.items():
        monkeypatch.setenv(variable, value)
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    response = app_module.create_app().test_client().get("/dev/test")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b'data-endpoint="/registro"' in response.data
    assert b'data-endpoint="/login"' in response.data


def test_development_test_page_is_absent_in_production(monkeypatch) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.setenv("FLASK_DEBUG", "0")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    response = app_module.create_app().test_client().get("/dev/test")

    assert response.status_code == 404


@pytest.mark.parametrize("variable", ["CLAIM_MASTER_KEY", "DEVICE_JWT_SECRET"])
def test_create_app_fails_with_name_of_missing_matera_variable(monkeypatch, variable) -> None:
    _set_fake_environment(monkeypatch)
    monkeypatch.delenv(variable)
    monkeypatch.setattr(app_module, "load_dotenv", Mock())

    with pytest.raises(ValueError, match=variable):
        app_module.create_app()
