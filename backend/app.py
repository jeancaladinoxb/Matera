import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, make_response, request, send_file

from backend.panelPrincipal.application.use_cases import (
    ConsultarPanelPrincipalCasoDeUso,
)
from backend.panelPrincipal.infrastructure.adapters import (
    PostgresMateraRepositoryAdapter as PostgresPanelMateraRepositoryAdapter,
    PostgresUsuarioRepositoryAdapter as PostgresPanelUsuarioRepositoryAdapter,
)
from backend.panelPrincipal.infrastructure.controllers import PanelPrincipalAdapter
from backend.materas.application.use_cases import (
    ActivarDispositivoUseCase,
    ConsultarMateraDelUsuarioUseCase,
    VincularMateraUseCase,
)
from backend.materas.infrastructure.adapters import PostgresMateraRepositoryAdapter
from backend.materas.infrastructure.adapters.hmac_claim_verifier import (
    hmac_claim_verifier_from_environment,
)
from backend.materas.infrastructure.adapters.jwt_device_token_adapter import (
    jwt_device_token_adapter_from_environment,
)
from backend.materas.infrastructure.controllers import MateraController
from backend.usuarios.application.use_cases import (
    IniciarSesionUseCase,
    RegistrarUsuarioUseCase,
)
from backend.usuarios.domain import InvalidTokenError
from backend.usuarios.infrastructure.adapters import (
    Argon2Hasher,
    JwtTokenAdapter,
    PostgresqlRepositoryAdapter,
)
from backend.usuarios.infrastructure.adapters.jwt_token_adapter import (
    jwt_token_adapter_from_environment,
)
from backend.usuarios.infrastructure.controllers import (
    SessionCookieSettings,
    WebAppController,
)
from backend.usuarios.infrastructure.adapters.postgresql_repository_adapter import (
    connection_factory_from_environment,
)


def create_app() -> Flask:
    load_dotenv(Path(__file__).resolve().parent / ".env")

    connection_factory = connection_factory_from_environment()
    usuario_repository = PostgresqlRepositoryAdapter(
        connection_factory
    )
    password_hasher = Argon2Hasher()
    token_provider: JwtTokenAdapter = jwt_token_adapter_from_environment()

    registrar_usuario = RegistrarUsuarioUseCase(
        usuario_repository,
        password_hasher,
        token_provider,
    )
    iniciar_sesion = IniciarSesionUseCase(
        usuario_repository,
        password_hasher,
        token_provider,
    )

    matera_repository = PostgresMateraRepositoryAdapter(connection_factory)
    claim_code_verifier = hmac_claim_verifier_from_environment()
    device_token_provider = jwt_device_token_adapter_from_environment()

    vincular_matera = VincularMateraUseCase(
        matera_repository, claim_code_verifier, token_provider
    )
    consultar_matera_del_usuario = ConsultarMateraDelUsuarioUseCase(
        matera_repository, token_provider
    )
    consultar_panel_principal = ConsultarPanelPrincipalCasoDeUso(
        PostgresPanelUsuarioRepositoryAdapter(connection_factory),
        PostgresPanelMateraRepositoryAdapter(connection_factory),
    )
    activar_dispositivo = ActivarDispositivoUseCase(
        matera_repository, claim_code_verifier, device_token_provider
    )

    app = Flask(__name__)
    _configure_cors(app)
    session_cookie_settings = _session_cookie_settings(token_provider)
    WebAppController(
        registrar_usuario,
        iniciar_sesion,
        token_provider,
        session_cookie_settings,
    ).register_routes(app)
    MateraController(
        vincular_matera,
        activar_dispositivo,
        consultar_matera_del_usuario,
        os.environ.get("SESSION_COOKIE_NAME", "cuida_mate_session"),
    ).register_routes(app)
    PanelPrincipalAdapter(
        consultar_panel_principal,
        lambda token: _session_usuario_id(token_provider, token),
        session_cookie_settings.name,
    ).register_routes(app)
    if _development_tools_enabled():
        test_page = Path(__file__).resolve().parent / "dev_tools" / "test_page.html"
        app.add_url_rule(
            "/dev/test",
            endpoint="development_test_page",
            view_func=lambda: send_file(test_page),
            methods=["GET"],
        )
    return app


def _session_usuario_id(
    token_provider: JwtTokenAdapter, token: str
) -> Optional[int]:
    try:
        return token_provider.verificar_token(token)
    except InvalidTokenError:
        return None


def _development_tools_enabled() -> bool:
    flask_debug = os.environ.get("FLASK_DEBUG", "").strip().lower()
    app_environment = os.environ.get("APP_ENV", "").strip().lower()
    return flask_debug in {"1", "true", "yes", "on"} or app_environment == "development"


def _session_cookie_settings(
    token_provider: JwtTokenAdapter,
) -> SessionCookieSettings:
    raw_secure = os.environ.get("SESSION_COOKIE_SECURE")
    if raw_secure is None:
        secure = os.environ.get("APP_ENV", "").strip().lower() == "production"
    else:
        normalized_secure = raw_secure.strip().lower()
        if normalized_secure not in {"1", "true", "yes", "on", "0", "false", "no", "off"}:
            raise ValueError("SESSION_COOKIE_SECURE debe ser un booleano.")
        secure = normalized_secure in {"1", "true", "yes", "on"}

    same_site = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax").strip()
    if same_site not in {"Strict", "Lax", "None"}:
        raise ValueError("SESSION_COOKIE_SAMESITE debe ser Strict, Lax o None.")
    if same_site == "None" and not secure:
        raise ValueError("SESSION_COOKIE_SECURE debe ser true con SameSite=None.")

    name = os.environ.get("SESSION_COOKIE_NAME", "cuida_mate_session").strip()
    if not name:
        raise ValueError("SESSION_COOKIE_NAME no puede estar vacío.")

    return SessionCookieSettings(
        name=name,
        max_age_seconds=token_provider.expiration_seconds,
        secure=secure,
        same_site=same_site,
    )


def _configure_cors(app: Flask) -> None:
    raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS")
    if raw_origins is None:
        if os.environ.get("APP_ENV", "").strip().lower() == "production":
            raise ValueError("CORS_ALLOWED_ORIGINS es obligatorio en producción.")
        origins = {"http://localhost:5173", "http://127.0.0.1:5173"}
    else:
        origins = {
            origin.strip()
            for origin in raw_origins.split(",")
            if origin.strip()
        }

    if not origins or "*" in origins:
        raise ValueError(
            "CORS_ALLOWED_ORIGINS debe contener orígenes explícitos; no se permite '*'."
        )

    @app.before_request
    def responder_preflight():
        if request.method == "OPTIONS":
            return make_response("", 204)
        return None

    @app.after_request
    def agregar_cabeceras_cors(response):
        origin = request.headers.get("Origin")
        if origin in origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            response.headers["Access-Control-Max-Age"] = "600"
            response.vary.add("Origin")
        return response


def main() -> None:
    create_app().run(port=5001)


if __name__ == "__main__":
    main()
