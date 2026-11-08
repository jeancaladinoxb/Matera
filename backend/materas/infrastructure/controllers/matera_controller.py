import logging
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, request

from backend.materas.application.ports.input import (
    ActivarDispositivoPort,
    VincularMateraPort,
)
from backend.materas.domain import (
    MateraNoVinculadaError,
    MateraOCodigoInvalidoError,
    MateraYaVinculadaError,
    ValidationError,
)
from backend.usuarios.domain import InvalidTokenError


logger = logging.getLogger(__name__)

_INVALID_MATERA_MESSAGE = "Matera o código inválido"


class MateraController:
    def __init__(
        self,
        vincular_matera: VincularMateraPort,
        activar_dispositivo: ActivarDispositivoPort,
    ) -> None:
        self._vincular_matera = vincular_matera
        self._activar_dispositivo = activar_dispositivo

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule(
            "/materas/vincular",
            endpoint="vincular_matera",
            view_func=self.vincular,
            methods=["POST"],
        )
        app.add_url_rule(
            "/dispositivos/activar",
            endpoint="activar_dispositivo",
            view_func=self.activar,
            methods=["POST"],
        )

    def vincular(self):
        token = self._bearer_token()
        if token is None:
            return self._unauthorized()

        body, error_response = self._read_json_body(("mac", "codigo"))
        if error_response is not None:
            return error_response

        try:
            self._vincular_matera.vincular(
                token=token, mac=body["mac"], codigo=body["codigo"]
            )
            return jsonify({"mensaje": "Matera vinculada"}), 200
        except InvalidTokenError:
            return self._unauthorized()
        except ValidationError as error:
            return jsonify({"error": str(error)}), 400
        except MateraOCodigoInvalidoError:
            return jsonify({"error": _INVALID_MATERA_MESSAGE}), 404
        except MateraYaVinculadaError:
            return jsonify({"error": "La matera ya está vinculada"}), 409
        except Exception as error:
            return self._internal_error(error)

    def activar(self):
        body, error_response = self._read_json_body(("mac", "codigo"))
        if error_response is not None:
            return error_response

        try:
            token = self._activar_dispositivo.activar(
                mac=body["mac"], codigo=body["codigo"]
            )
            response = jsonify({"token": token})
            # Keep proxies from caching a response that carries a token.
            response.headers["Cache-Control"] = "no-store"
            return response, 200
        except ValidationError as error:
            return jsonify({"error": str(error)}), 400
        except MateraOCodigoInvalidoError:
            return jsonify({"error": _INVALID_MATERA_MESSAGE}), 404
        except MateraNoVinculadaError:
            return jsonify({"error": "La matera aún no está vinculada"}), 409
        except Exception as error:
            return self._internal_error(error)

    @staticmethod
    def _bearer_token() -> Optional[str]:
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        token = token.strip()
        if scheme.lower() != "bearer" or not token:
            return None
        return token

    @staticmethod
    def _unauthorized():
        return jsonify({"error": "No autorizado"}), 401

    @staticmethod
    def _internal_error(error: Exception):
        # Includes RepositoryError: logged by type only, generic to the client.
        logger.error("Matera request failed unexpectedly (%s).", type(error).__name__)
        return jsonify({"error": "Error interno del servidor"}), 500

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
