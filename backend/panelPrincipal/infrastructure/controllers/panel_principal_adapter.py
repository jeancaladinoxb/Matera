import logging
from typing import Callable, Optional

from flask import Flask, jsonify, request

from backend.panelPrincipal.application.ports.input import (
    ConsultarPanelPrincipalPort,
)
from backend.panelPrincipal.application.resultado_consulta_panel import (
    ConsultaPanelExitosa,
    ConsultaPanelFallida,
    ErrorConsultaPanel,
)


logger = logging.getLogger(__name__)


class PanelPrincipalAdapter:
    def __init__(
        self,
        consultar_panel: ConsultarPanelPrincipalPort,
        resolver_usuario_id: Callable[[str], Optional[int]],
        session_cookie_name: str,
    ) -> None:
        self._consultar_panel = consultar_panel
        self._resolver_usuario_id = resolver_usuario_id
        self._session_cookie_name = session_cookie_name

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule(
            "/panel",
            endpoint="consultar_panel_principal",
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
                "Panel authentication failed unexpectedly (%s).",
                type(error).__name__,
            )
            return self._internal_error()
        if usuario_id is None:
            return self._unauthorized()

        try:
            resultado = self._consultar_panel.consultar(usuario_id)
        except Exception as error:
            logger.error(
                "Panel request failed unexpectedly (%s).",
                type(error).__name__,
            )
            return self._internal_error()

        if isinstance(resultado, ConsultaPanelExitosa):
            return self._panel_response(resultado)
        if isinstance(resultado, ConsultaPanelFallida):
            return self._error_response(resultado.error)
        return self._internal_error()

    @staticmethod
    def _panel_response(resultado: ConsultaPanelExitosa):
        panel = resultado.panel
        response = jsonify(
            {
                "usuario": {
                    "usuario_id": panel.usuario.usuario_id,
                    "nombre": panel.usuario.nombre,
                    "nickname": panel.usuario.nickname,
                },
                "materas": [
                    {
                        "matera_id": matera.matera_id,
                        "dispositivo_id": matera.dispositivo_id,
                        "mac": matera.mac,
                        "planta_id": matera.planta_id,
                    }
                    for matera in panel.materas
                ],
            }
        )
        response.headers["Cache-Control"] = "no-store"
        return response, 200

    @classmethod
    def _error_response(cls, error: ErrorConsultaPanel):
        if error is ErrorConsultaPanel.USUARIO_NO_ENCONTRADO:
            return jsonify({"error": "Recurso no encontrado"}), 404
        return cls._internal_error()

    @staticmethod
    def _unauthorized():
        return jsonify({"error": "No autorizado"}), 401

    @staticmethod
    def _internal_error():
        return jsonify({"error": "Error interno del servidor"}), 500
