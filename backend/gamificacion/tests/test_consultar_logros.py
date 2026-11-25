import unittest
from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.gamificacion.application import (
    ConsultaLogrosExitosa,
    ConsultaLogrosFallida,
    ErrorConsultaLogros,
)
from backend.gamificacion.application.errors import (
    ErrorAccesoDatosGamificacionError,
)
from backend.gamificacion.application.ports.output import (
    EstadisticasRepositoryPort,
    RelojPort,
)
from backend.gamificacion.application.use_cases import ConsultarLogrosCasoDeUso
from backend.gamificacion.domain import EstadisticasJardinero


AHORA = datetime(2026, 11, 24, tzinfo=timezone.utc)


class FakeEstadisticasRepository(EstadisticasRepositoryPort):
    def __init__(self) -> None:
        self.estadisticas: Optional[EstadisticasJardinero] = EstadisticasJardinero(
            7, AHORA - timedelta(days=10), (AHORA - timedelta(days=9, hours=23),)
        )
        self.error: Optional[Exception] = None

    def obtener_por_usuario(self, usuario_id: int) -> Optional[EstadisticasJardinero]:
        if self.error is not None:
            raise self.error
        return self.estadisticas


class FakeReloj(RelojPort):
    def ahora(self) -> datetime:
        return AHORA


class ConsultarLogrosCasoDeUsoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = FakeEstadisticasRepository()
        self.caso_de_uso = ConsultarLogrosCasoDeUso(self.repository, FakeReloj())

    def test_devuelve_el_perfil_evaluado(self) -> None:
        resultado = self.caso_de_uso.consultar(7)

        self.assertIsInstance(resultado, ConsultaLogrosExitosa)
        self.assertEqual(resultado.perfil.usuario_id, 7)
        self.assertEqual(resultado.perfil.puntos, 25)

    def test_usuario_inexistente_o_de_otro_id(self) -> None:
        self.repository.estadisticas = None
        self.assertEqual(
            self.caso_de_uso.consultar(7),
            ConsultaLogrosFallida(ErrorConsultaLogros.USUARIO_NO_ENCONTRADO),
        )
        self.repository.estadisticas = EstadisticasJardinero(99, AHORA, ())
        self.assertEqual(
            self.caso_de_uso.consultar(7),
            ConsultaLogrosFallida(ErrorConsultaLogros.USUARIO_NO_ENCONTRADO),
        )

    def test_traduce_errores_de_datos_y_desconocidos(self) -> None:
        self.repository.error = ErrorAccesoDatosGamificacionError()
        self.assertEqual(
            self.caso_de_uso.consultar(7),
            ConsultaLogrosFallida(ErrorConsultaLogros.ERROR_ACCESO_DATOS),
        )
        self.repository.error = RuntimeError("boom")
        self.assertEqual(
            self.caso_de_uso.consultar(7),
            ConsultaLogrosFallida(ErrorConsultaLogros.ERROR_DESCONOCIDO),
        )


if __name__ == "__main__":
    unittest.main()
