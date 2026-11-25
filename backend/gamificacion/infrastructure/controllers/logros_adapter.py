import logging
from typing import Callable, Optional

from flask import Flask, jsonify, request

from backend.gamificacion.application.ports.input import ConsultarLogrosPort
from backend.gamificacion.application.resultado_consulta_logros import (
    ConsultaLogrosExitosa,
    ConsultaLogrosFallida,
    ErrorConsultaLogros,
)
from backend.gamificacion.domain import PerfilGamificacion


logger = logging.getLogger(__name__)


class LogrosAdapter:
    def __init__(
        self,
        consultar_logros: ConsultarLogrosPort,
        resolver_usuario_id: Callable[[str], Optional[int]],
        session_cookie_name: str,
    ) -> None:
        self._consultar_logros = consultar_logros
        self._resolver_usuario_id = resolver_usuario_id
        self._session_cookie_name = session_cookie_name

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule(
            "/logros",
            endpoint="consultar_logros",
            view_func=self.consultar,
            methods=["GET"],
        )

    def consultar(self):
        token = request.cookies.get(self._session_cookie_name)
        if token is None:
            return self._unauthorized()

        try:
            usuario_id = self._resolver_usuario_id(token)
        except Exception as error:
            logger.error(
                "Gamification authentication failed unexpectedly (%s).",
                type(error).__name__,
            )
            return self._internal_error()
        if usuario_id is None:
            return self._unauthorized()

        try:
            resultado = self._consultar_logros.consultar(usuario_id)
        except Exception as error:
            logger.error(
                "Gamification request failed unexpectedly (%s).",
                type(error).__name__,
            )
            return self._internal_error()

        if isinstance(resultado, ConsultaLogrosExitosa):
            return self._perfil_response(resultado.perfil)
        if isinstance(resultado, ConsultaLogrosFallida):
            return self._error_response(resultado.error)
        return self._internal_error()

    @staticmethod
    def _perfil_response(perfil: PerfilGamificacion):
        siguiente = perfil.siguiente_nivel
        response = jsonify(
            {
                "puntos": perfil.puntos,
                "nivel": {
                    "numero": perfil.nivel.numero,
                    "nombre": perfil.nivel.nombre,
                    "puntos_minimos": perfil.nivel.puntos_minimos,
                },
                "siguiente_nivel": None
                if siguiente is None
                else {
                    "numero": siguiente.numero,
                    "nombre": siguiente.nombre,
                    "puntos_minimos": siguiente.puntos_minimos,
                },
                "logros": [
                    {
                        "codigo": logro.codigo,
                        "nombre": logro.nombre,
                        "descripcion": logro.descripcion,
                        "icono": logro.icono,
                        "puntos": logro.puntos,
                        "progreso": logro.progreso,
                        "meta": logro.meta,
                        "desbloqueado": logro.desbloqueado,
                        "fecha_desbloqueo": None
                        if logro.fecha_desbloqueo is None
                        else logro.fecha_desbloqueo.isoformat(),
                    }
                    for logro in perfil.logros
                ],
            }
        )
        response.headers["Cache-Control"] = "no-store"
        return response, 200

    @classmethod
    def _error_response(cls, error: ErrorConsultaLogros):
        if error is ErrorConsultaLogros.USUARIO_NO_ENCONTRADO:
            return jsonify({"error": "Recurso no encontrado"}), 404
        return cls._internal_error()

    @staticmethod
    def _unauthorized():
        return jsonify({"error": "No autorizado"}), 401

    @staticmethod
    def _internal_error():
        return jsonify({"error": "Error interno del servidor"}), 500
