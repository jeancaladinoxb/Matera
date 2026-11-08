import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, send_file

from backend.materas.application.use_cases import (
    ActivarDispositivoUseCase,
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
from backend.usuarios.infrastructure.adapters import (
    Argon2Hasher,
    JwtTokenAdapter,
    PostgresqlRepositoryAdapter,
)
from backend.usuarios.infrastructure.adapters.jwt_token_adapter import (
    jwt_token_adapter_from_environment,
)
from backend.usuarios.infrastructure.controllers import WebAppController
from backend.usuarios.infrastructure.adapters.postgresql_repository_adapter import (
    connection_factory_from_environment,
)


def create_app() -> Flask:
    load_dotenv(Path(__file__).resolve().parent / ".env")

    usuario_repository = PostgresqlRepositoryAdapter(
        connection_factory_from_environment()
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

    connection_factory = connection_factory_from_environment()
    matera_repository = PostgresMateraRepositoryAdapter(connection_factory)
    claim_code_verifier = hmac_claim_verifier_from_environment()
    device_token_provider = jwt_device_token_adapter_from_environment()

    vincular_matera = VincularMateraUseCase(
        matera_repository, claim_code_verifier, token_provider
    )
    activar_dispositivo = ActivarDispositivoUseCase(
        matera_repository, claim_code_verifier, device_token_provider
    )

    app = Flask(__name__)
    WebAppController(registrar_usuario, iniciar_sesion).register_routes(app)
    MateraController(vincular_matera, activar_dispositivo).register_routes(app)
    if _development_tools_enabled():
        test_page = Path(__file__).resolve().parent / "dev_tools" / "test_page.html"
        app.add_url_rule(
            "/dev/test",
            endpoint="development_test_page",
            view_func=lambda: send_file(test_page),
            methods=["GET"],
        )
    return app


def _development_tools_enabled() -> bool:
    flask_debug = os.environ.get("FLASK_DEBUG", "").strip().lower()
    app_environment = os.environ.get("APP_ENV", "").strip().lower()
    return flask_debug in {"1", "true", "yes", "on"} or app_environment == "development"


def main() -> None:
    create_app().run(port=5001)


if __name__ == "__main__":
    main()
