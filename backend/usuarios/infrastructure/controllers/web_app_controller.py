import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, make_response, request

from backend.usuarios.application.ports.input import (
    IniciarSesionPort,
    RegistrarUsuarioPort,
)
from backend.usuarios.application.ports.output import TokenProviderPort
from backend.usuarios.domain import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    ValidationError,
)


logger = logging.getLogger(__name__)
_SESSION_COOKIE_NAME = "cuida_mate_session"


@dataclass(frozen=True)
class SessionCookieSettings:
    name: str
    max_age_seconds: int
    secure: bool
    same_site: str


class WebAppController:
    def __init__(
        self,
        registrar_usuario: RegistrarUsuarioPort,
        iniciar_sesion: IniciarSesionPort,
        token_provider: TokenProviderPort,
        session_cookie: SessionCookieSettings,
    ) -> None:
        self._registrar_usuario = registrar_usuario
        self._iniciar_sesion = iniciar_sesion
        self._token_provider = token_provider
        self._session_cookie = session_cookie

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
        app.add_url_rule(
            "/session/refresh",
            endpoint="refrescar_sesion",
            view_func=self.refrescar_sesion,
            methods=["POST"],
        )
        app.add_url_rule(
            "/logout",
            endpoint="cerrar_sesion",
            view_func=self.cerrar_sesion,
            methods=["POST"],
        )

    def registrar(self):
        body, error_response = self._read_json_body(
            ("nombre", "apellido", "nickname", "correo", "contrasena")
        )
        if error_response is not None:
            return error_response

        try:
            self._registrar_usuario.registrar(
                nombre=body["nombre"],
                apellido=body["apellido"],
                nickname=body["nickname"],
                correo=body["correo"],
                contrasena=body["contrasena"],
            )
            response = jsonify({"mensaje": "Registro exitoso"})
            response.status_code = 201
            response.headers["Cache-Control"] = "no-store"
            return response
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
            response = self._session_response(token, 200, "Inicio de sesión exitoso")
            return response
        except InvalidCredentialsError:
            return jsonify({"error": "Credenciales inválidas"}), 401
        except Exception as error:
            self._log_unexpected_error(error)
            return jsonify({"error": "Error interno del servidor"}), 500

    def refrescar_sesion(self):
        token = request.cookies.get(self._session_cookie.name)
        try:
            usuario_id = self._token_provider.verificar_token(token or "")
        except InvalidTokenError:
            return (
                jsonify(
                    {
                        "error": "La sesión no se puede renovar",
                        "codigo": "SESION_RECHAZADA",
                    }
                ),
                401,
            )
        except Exception as error:
            self._log_unexpected_error(error)
            return jsonify({"error": "Error interno del servidor"}), 500

        nuevo_token = self._token_provider.generar_token(usuario_id)
        return self._session_response(nuevo_token, 200, "Sesión renovada")

    def cerrar_sesion(self):
        response = make_response("", 204)
        response.delete_cookie(
            self._session_cookie.name,
            path="/",
            secure=self._session_cookie.secure,
            httponly=True,
            samesite=self._session_cookie.same_site,
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    def _session_response(self, token: str, status: int, mensaje: str):
        response = jsonify({"mensaje": mensaje})
        response.status_code = status
        response.set_cookie(
            self._session_cookie.name,
            token,
            max_age=self._session_cookie.max_age_seconds,
            path="/",
            secure=self._session_cookie.secure,
            httponly=True,
            samesite=self._session_cookie.same_site,
        )
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
