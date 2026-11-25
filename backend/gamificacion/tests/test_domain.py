import unittest
from datetime import datetime, timedelta, timezone

from backend.gamificacion.domain import (
    EstadisticasInvalidasError,
    EstadisticasJardinero,
    EvaluadorDeLogros,
    Logro,
    LogroInvalidoError,
    PerfilGamificacion,
    nivel_para,
)


REGISTRO = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


def _estadisticas(*horas_tras_registro: float) -> EstadisticasJardinero:
    return EstadisticasJardinero(
        usuario_id=7,
        fecha_registro=REGISTRO,
        fechas_vinculacion=tuple(
            REGISTRO + timedelta(hours=horas) for horas in horas_tras_registro
        ),
    )


def _por_codigo(perfil: PerfilGamificacion) -> dict:
    return {logro.codigo: logro for logro in perfil.logros}


class EstadisticasJardineroTests(unittest.TestCase):
    def test_ordena_las_fechas_de_vinculacion(self) -> None:
        estadisticas = _estadisticas(50, 2, 10)

        self.assertEqual(estadisticas.materas_vinculadas, 3)
        self.assertEqual(estadisticas.primera_vinculacion, REGISTRO + timedelta(hours=2))
        self.assertEqual(estadisticas.fecha_vinculacion_numero(3), REGISTRO + timedelta(hours=50))
        self.assertIsNone(estadisticas.fecha_vinculacion_numero(4))

    def test_rechaza_datos_invalidos(self) -> None:
        sin_zona = datetime(2026, 10, 1)
        casos = [
            dict(usuario_id=0, fecha_registro=REGISTRO, fechas_vinculacion=()),
            dict(usuario_id=True, fecha_registro=REGISTRO, fechas_vinculacion=()),
            dict(usuario_id=7, fecha_registro=sin_zona, fechas_vinculacion=()),
            dict(usuario_id=7, fecha_registro=REGISTRO, fechas_vinculacion=(sin_zona,)),
            dict(usuario_id=7, fecha_registro=REGISTRO, fechas_vinculacion="x"),
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                with self.assertRaises(EstadisticasInvalidasError):
                    EstadisticasJardinero(**datos)


class LogroTests(unittest.TestCase):
    def test_limita_el_progreso_a_la_meta(self) -> None:
        logro = Logro("a", "A", "desc", "🌱", 10, progreso=4, meta=1)

        self.assertEqual(logro.progreso, 1)
        self.assertFalse(logro.desbloqueado)

    def test_rechaza_meta_cero_o_valores_negativos(self) -> None:
        with self.assertRaises(LogroInvalidoError):
            Logro("a", "A", "desc", "🌱", 10, progreso=0, meta=0)
        with self.assertRaises(LogroInvalidoError):
            Logro("a", "A", "desc", "🌱", -1, progreso=0, meta=1)
        with self.assertRaises(LogroInvalidoError):
            Logro("", "A", "desc", "🌱", 1, progreso=0, meta=1)


class EvaluadorDeLogrosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluador = EvaluadorDeLogros()

    def test_usuario_sin_materas_no_tiene_logros(self) -> None:
        perfil = self.evaluador.evaluar(_estadisticas(), REGISTRO + timedelta(days=90))

        self.assertEqual(perfil.puntos, 0)
        self.assertEqual(perfil.logros_desbloqueados, 0)
        self.assertEqual(perfil.nivel.nombre, "Semilla")
        self.assertEqual(perfil.puntos_para_siguiente_nivel, 20)

    def test_primera_matera_rapida_desbloquea_primer_brote_y_expres(self) -> None:
        ahora = REGISTRO + timedelta(days=2)
        perfil = self.evaluador.evaluar(_estadisticas(3), ahora)
        logros = _por_codigo(perfil)

        self.assertTrue(logros["primer_brote"].desbloqueado)
        self.assertEqual(
            logros["primer_brote"].fecha_desbloqueo, REGISTRO + timedelta(hours=3)
        )
        self.assertTrue(logros["vinculacion_expres"].desbloqueado)
        self.assertFalse(logros["jardin_en_casa"].desbloqueado)
        self.assertEqual(logros["jardin_en_casa"].progreso, 1)
        self.assertEqual(perfil.puntos, 25)
        self.assertEqual(perfil.nivel.nombre, "Brote")

    def test_vinculacion_despues_de_24_horas_no_es_expres(self) -> None:
        perfil = self.evaluador.evaluar(_estadisticas(25), REGISTRO + timedelta(days=3))

        self.assertFalse(_por_codigo(perfil)["vinculacion_expres"].desbloqueado)

    def test_un_mes_cuidando_usa_la_fecha_de_la_primera_matera(self) -> None:
        estadisticas = _estadisticas(30)
        primera = REGISTRO + timedelta(hours=30)

        antes = _por_codigo(
            self.evaluador.evaluar(estadisticas, primera + timedelta(days=29))
        )["un_mes_cuidando"]
        despues = _por_codigo(
            self.evaluador.evaluar(estadisticas, primera + timedelta(days=45))
        )["un_mes_cuidando"]

        self.assertFalse(antes.desbloqueado)
        self.assertEqual(antes.progreso, 29)
        self.assertTrue(despues.desbloqueado)
        self.assertEqual(despues.progreso, 30)
        self.assertEqual(despues.fecha_desbloqueo, primera + timedelta(days=30))

    def test_cinco_materas_y_un_mes_llega_a_maestro_jardinero(self) -> None:
        perfil = self.evaluador.evaluar(
            _estadisticas(1, 2, 3, 4, 5), REGISTRO + timedelta(days=60)
        )

        self.assertEqual(perfil.logros_desbloqueados, 5)
        self.assertEqual(perfil.puntos, 120)
        self.assertEqual(perfil.nivel.nombre, "Maestro jardinero")
        self.assertIsNone(perfil.siguiente_nivel)
        self.assertEqual(perfil.puntos_para_siguiente_nivel, 0)

    def test_el_resultado_no_cambia_entre_consultas_una_vez_desbloqueado(self) -> None:
        estadisticas = _estadisticas(1, 2, 3)
        primera = self.evaluador.evaluar(estadisticas, REGISTRO + timedelta(days=5))
        luego = self.evaluador.evaluar(estadisticas, REGISTRO + timedelta(days=6))

        self.assertEqual(
            _por_codigo(primera)["jardin_en_casa"].fecha_desbloqueo,
            _por_codigo(luego)["jardin_en_casa"].fecha_desbloqueo,
        )

    def test_rechaza_fecha_actual_sin_zona(self) -> None:
        with self.assertRaises(Exception):
            self.evaluador.evaluar(_estadisticas(), datetime(2026, 11, 1))


class NivelTests(unittest.TestCase):
    def test_umbrales(self) -> None:
        self.assertEqual(nivel_para(0).nombre, "Semilla")
        self.assertEqual(nivel_para(19).nombre, "Semilla")
        self.assertEqual(nivel_para(20).nombre, "Brote")
        self.assertEqual(nivel_para(50).nombre, "Plántula")
        self.assertEqual(nivel_para(90).nombre, "Jardinero")
        self.assertEqual(nivel_para(500).nombre, "Maestro jardinero")


if __name__ == "__main__":
    unittest.main()
