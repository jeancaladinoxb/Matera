import logging
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, request

from backend.plantas.application.ports.input import (
    ListarPlantasPort,
    VincularPlantaAMateraPort,
)
from backend.plantas.domain import (
    MateraNoEncontradaError,
    PlantaNoEncontradaError,
    ValidationError,
)
from backend.usuarios.domain import InvalidTokenError


logger = logging.getLogger(__name__)

# One message for an unknown plant and for an unknown or foreign matera.
_NOT_FOUND_MESSAGE = "Recurso no encontrado"


class PlantaController:
    def __init__(
        self,
        listar_plantas: ListarPlantasPort,
        vincular_planta: VincularPlantaAMateraPort,
        session_cookie_name: str = "cuida_mate_session",
    ) -> None:
        self._listar_plantas = listar_plantas
        self._vincular_planta = vincular_planta
        self._session_cookie_name = session_cookie_name

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule(
            "/plantas",
            endpoint="listar_plantas",
            view_func=self.listar,
            methods=["GET"],
        )
        app.add_url_rule(
            "/materas/<int:matera_id>/planta",
            endpoint="vincular_planta_a_matera",
            view_func=self.vincular,
            methods=["POST"],
        )

    def listar(self):
        token = request.cookies.get(self._session_cookie_name)
        if token is None:
            return self._unauthorized()

        try:
            plantas = self._listar_plantas.listar(token)
            return (
                jsonify(
                    {
                        "plantas": [
                            {
                                "id": planta.id,
                                "slug": planta.slug,
                                "nombre_comun": planta.nombre_comun,
                                "nombre_cientifico": planta.nombre_cientifico,
                                "luz": planta.luz.value,
                                "riego": planta.riego.value,
                            }
                            for planta in plantas
                        ]
                    }
                ),
                200,
            )
        except InvalidTokenError:
            return self._unauthorized()
        except Exception as error:
            return self._internal_error(error)

    def vincular(self, matera_id: int):
        token = request.cookies.get(self._session_cookie_name)
        if token is None:
            return self._unauthorized()

        planta_id, error_response = self._read_planta_id()
        if error_response is not None:
            return error_response

        try:
            self._vincular_planta.vincular(token, matera_id, planta_id)
            return (
                jsonify(
                    {
                        "mensaje": "Planta vinculada",
                        "matera_id": matera_id,
                        "planta_id": planta_id,
                    }
                ),
                200,
            )
        except InvalidTokenError:
            return self._unauthorized()
        except ValidationError as error:
            return jsonify({"error": str(error)}), 400
        except (PlantaNoEncontradaError, MateraNoEncontradaError):
            return jsonify({"error": _NOT_FOUND_MESSAGE}), 404
        except Exception as error:
            return self._internal_error(error)

    @staticmethod
    def _unauthorized():
        return jsonify({"error": "No autorizado"}), 401

    @staticmethod
    def _internal_error(error: Exception):
        # Includes RepositoryError: logged by type only, generic to the client.
        logger.error("Planta request failed unexpectedly (%s).", type(error).__name__)
        return jsonify({"error": "Error interno del servidor"}), 500

    @staticmethod
    def _read_planta_id() -> Tuple[Optional[int], Optional[Tuple[Any, int]]]:
        if not request.is_json:
            return None, (jsonify({"error": "Se requiere un cuerpo JSON válido"}), 400)

        body: Optional[Dict[str, Any]] = request.get_json(silent=True)
        if not isinstance(body, dict):
            return None, (jsonify({"error": "Se requiere un cuerpo JSON válido"}), 400)

        if "planta_id" not in body:
            return None, (jsonify({"error": "Faltan campos obligatorios"}), 400)

        planta_id = body["planta_id"]
        # bool es subclase de int: se rechaza de forma explícita
        if isinstance(planta_id, bool) or not isinstance(planta_id, int) or planta_id <= 0:
            return None, (
                jsonify({"error": "planta_id debe ser un entero positivo"}),
                400,
            )
        return planta_id, None
