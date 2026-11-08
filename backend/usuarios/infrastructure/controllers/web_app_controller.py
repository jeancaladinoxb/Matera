import logging
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, request

from backend.usuarios.application.ports.input import (
    IniciarSesionPort,
    RegistrarUsuarioPort,
)
from backend.usuarios.domain import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    ValidationError,
)


logger = logging.getLogger(__name__)


class WebAppController:
    def __init__(
        self,
        registrar_usuario: RegistrarUsuarioPort,
        iniciar_sesion: IniciarSesionPort,
    ) -> None:
        self._registrar_usuario = registrar_usuario
        self._iniciar_sesion = iniciar_sesion

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule(
            "/registro",
            endpoint="registrar_usuario",
            view_func=self.registrar,
            methods=["POST"],
        )
        app.add_url_rule(
            "/login",
            endpoint="iniciar_sesion",
            view_func=self.iniciar_sesion,
            methods=["POST"],
        )

    def registrar(self):
        body, error_response = self._read_json_body(
            ("nombre", "apellido", "nickname", "correo", "contrasena")
        )
        if error_response is not None:
            return error_response

        try:
            token = self._registrar_usuario.registrar(
                nombre=body["nombre"],
                apellido=body["apellido"],
                nickname=body["nickname"],
                correo=body["correo"],
                contrasena=body["contrasena"],
            )
            return self._token_response(token, 201)
        except ValidationError as error:
            return jsonify({"error": str(error)}), 400
        except EmailAlreadyRegisteredError:
            return jsonify({"error": "No se pudo completar el registro"}), 400
        except Exception as error:
            # Includes RepositoryError: all unexpected failures look the same
            # to the client and are logged by type only.
            self._log_unexpected_error(error)
            return jsonify({"error": "Error interno del servidor"}), 500

    def iniciar_sesion(self):
        body, error_response = self._read_json_body(("correo", "contrasena"))
        if error_response is not None:
            return error_response

        try:
            token = self._iniciar_sesion.iniciar_sesion(
                correo=body["correo"],
                contrasena=body["contrasena"],
            )
            return self._token_response(token, 200)
        except InvalidCredentialsError:
            return jsonify({"error": "Credenciales inválidas"}), 401
        except Exception as error:
            self._log_unexpected_error(error)
            return jsonify({"error": "Error interno del servidor"}), 500

    @staticmethod
    def _token_response(token: str, status: int):
        response = jsonify({"token": token})
        response.status_code = status
        # Keep proxies and browsers from caching a response that carries a token.
        response.headers["Cache-Control"] = "no-store"
        return response

    @staticmethod
    def _read_json_body(
        required_fields: Tuple[str, ...],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Any, int]]]:
        if not request.is_json:
            return None, (jsonify({"error": "Se requiere un cuerpo JSON válido"}), 400)

        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return None, (jsonify({"error": "Se requiere un cuerpo JSON válido"}), 400)

        if any(field not in body for field in required_fields):
            return None, (jsonify({"error": "Faltan campos obligatorios"}), 400)

        if any(not isinstance(body[field], str) for field in required_fields):
            return None, (jsonify({"error": "Los campos deben ser texto"}), 400)

        return body, None

    @staticmethod
    def _log_unexpected_error(error: Exception) -> None:
        logger.error(
            "User request failed unexpectedly (%s).",
            type(error).__name__,
        )
