import unittest
from datetime import datetime, timezone

from flask import Flask

from backend.gamificacion.application import (
    ConsultaLogrosExitosa,
    ConsultaLogrosFallida,
    ErrorConsultaLogros,
    ResultadoConsultarLogros,
)
from backend.gamificacion.application.ports.input import ConsultarLogrosPort
from backend.gamificacion.domain import Logro, PerfilGamificacion
from backend.gamificacion.infrastructure.controllers import LogrosAdapter


FECHA = datetime(2026, 11, 1, 15, 30, tzinfo=timezone.utc)


class FakeConsultarLogros(ConsultarLogrosPort):
    def __init__(self) -> None:
        self.resultado: ResultadoConsultarLogros = ConsultaLogrosExitosa(
            PerfilGamificacion(
                7,
                (
                    Logro("primer_brote", "Primer brote", "Vincula tu primera matera.",
                          "🌱", 10, 1, 1, FECHA),
                    Logro("jardin_en_casa", "Jardín en casa", "Ten 3 materas vinculadas.",
                          "🪴", 25, 1, 3, None),
                ),
            )
        )
        self.usuario_ids = []

    def consultar(self, usuario_id: int) -> ResultadoConsultarLogros:
        self.usuario_ids.append(usuario_id)
        return self.resultado


class LogrosAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.consultar = FakeConsultarLogros()
        self.app = Flask(__name__)
        LogrosAdapter(
            self.consultar,
            lambda token: 7 if token == "valid-token" else None,
            "cuida_mate_session",
        ).register_routes(self.app)
        self.client = self.app.test_client()

    def test_devuelve_puntos_nivel_y_logros_del_usuario_de_la_sesion(self) -> None:
        self.client.set_cookie("cuida_mate_session", "valid-token")

        response = self.client.get("/logros?usuario_id=99")

        self.assertEqual(response.status_code, 200)
        cuerpo = response.get_json()
        self.assertEqual(cuerpo["puntos"], 10)
        self.assertEqual(cuerpo["nivel"], {"numero": 1, "nombre": "Semilla", "puntos_minimos": 0})
        self.assertEqual(cuerpo["siguiente_nivel"]["nombre"], "Brote")
        self.assertEqual(
            cuerpo["logros"][0],
            {
                "codigo": "primer_brote",
                "nombre": "Primer brote",
                "descripcion": "Vincula tu primera matera.",
                "icono": "🌱",
                "puntos": 10,
                "progreso": 1,
                "meta": 1,
                "desbloqueado": True,
                "fecha_desbloqueo": "2026-11-01T15:30:00+00:00",
            },
        )
        self.assertIsNone(cuerpo["logros"][1]["fecha_desbloqueo"])
        self.assertEqual(self.consultar.usuario_ids, [7])
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_sin_sesion_o_sesion_invalida_devuelve_401(self) -> None:
        self.assertEqual(self.client.get("/logros").status_code, 401)
        self.client.set_cookie("cuida_mate_session", "otro")
        self.assertEqual(self.client.get("/logros").status_code, 401)
        self.assertEqual(self.consultar.usuario_ids, [])

    def test_errores_del_caso_de_uso(self) -> None:
        self.client.set_cookie("cuida_mate_session", "valid-token")
        self.consultar.resultado = ConsultaLogrosFallida(
            ErrorConsultaLogros.USUARIO_NO_ENCONTRADO
        )
        self.assertEqual(self.client.get("/logros").status_code, 404)
        self.consultar.resultado = ConsultaLogrosFallida(
            ErrorConsultaLogros.ERROR_ACCESO_DATOS
        )
        response = self.client.get("/logros")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Error interno del servidor"})


if __name__ == "__main__":
    unittest.main()
