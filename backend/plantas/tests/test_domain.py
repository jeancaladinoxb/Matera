import dataclasses
import unittest

from backend.plantas.domain import (
    NivelLuz,
    NivelRiego,
    Planta,
    PlantaIdInvalidoError,
    PlantaInvalidaError,
    ValidationError,
    es_entero_positivo,
)


def crear_planta(**cambios) -> Planta:
    datos = dict(
        id=1,
        slug="monstera",
        nombre_comun="Monstera",
        nombre_cientifico="Monstera deliciosa",
        luz="indirecta",
        riego="moderado",
        humedad_suelo_min=40,
        humedad_suelo_max=60,
        temperatura_min=18,
        temperatura_max=30,
        luz_lux_min=8000,
        luz_lux_max=20000,
    )
    datos.update(cambios)
    return Planta(**datos)


class PlantaTests(unittest.TestCase):
    def test_planta_valida_normaliza_luz_y_riego(self) -> None:
        planta = crear_planta()

        self.assertIs(planta.luz, NivelLuz.INDIRECTA)
        self.assertIs(planta.riego, NivelRiego.MODERADO)
        self.assertEqual(planta.slug, "monstera")

    def test_es_inmutable(self) -> None:
        with self.assertRaises(dataclasses.FrozenInstanceError):
            crear_planta().slug = "otra"  # type: ignore[misc]

    def test_id_debe_ser_entero_positivo(self) -> None:
        for invalido in (0, -1, True, False, "1", 1.0, None):
            with self.subTest(id=invalido):
                with self.assertRaises(PlantaIdInvalidoError):
                    crear_planta(id=invalido)

    def test_slug_solo_minusculas_numeros_y_guion_bajo(self) -> None:
        for valido in ("monstera", "ficus_2", "a1"):
            with self.subTest(slug=valido):
                self.assertEqual(crear_planta(slug=valido).slug, valido)
        for invalido in ("", "Monstera", "mon-stera", "mon stera", "monstera\n", "ñandú", None):
            with self.subTest(slug=invalido):
                with self.assertRaises(PlantaInvalidaError):
                    crear_planta(slug=invalido)

    def test_nombres_obligatorios(self) -> None:
        for campo in ("nombre_comun", "nombre_cientifico"):
            for invalido in ("", "   ", None, 3):
                with self.subTest(campo=campo, valor=invalido):
                    with self.assertRaises(PlantaInvalidaError):
                        crear_planta(**{campo: invalido})

    def test_luz_y_riego_validos(self) -> None:
        for luz in ("baja", "indirecta", "directa"):
            self.assertEqual(crear_planta(luz=luz).luz.value, luz)
        for riego in ("bajo", "moderado", "alto"):
            self.assertEqual(crear_planta(riego=riego).riego.value, riego)
        with self.assertRaises(PlantaInvalidaError):
            crear_planta(luz="sol")
        with self.assertRaises(PlantaInvalidaError):
            crear_planta(riego="mucho")

    def test_minimo_debe_ser_menor_que_el_maximo_en_cada_rango(self) -> None:
        casos = (
            dict(humedad_suelo_min=60, humedad_suelo_max=60),
            dict(humedad_suelo_min=70, humedad_suelo_max=60),
            dict(temperatura_min=30, temperatura_max=30),
            dict(temperatura_min=31, temperatura_max=30),
            dict(luz_lux_min=20000, luz_lux_max=20000),
            dict(luz_lux_min=30000, luz_lux_max=20000),
        )
        for cambios in casos:
            with self.subTest(cambios=cambios):
                with self.assertRaises(PlantaInvalidaError):
                    crear_planta(**cambios)

    def test_humedad_entre_0_y_100(self) -> None:
        self.assertEqual(crear_planta(humedad_suelo_min=0, humedad_suelo_max=100).humedad_suelo_max, 100)
        with self.assertRaises(PlantaInvalidaError):
            crear_planta(humedad_suelo_min=-1)
        with self.assertRaises(PlantaInvalidaError):
            crear_planta(humedad_suelo_max=101)

    def test_luz_no_negativa_y_rangos_numericos(self) -> None:
        with self.assertRaises(PlantaInvalidaError):
            crear_planta(luz_lux_min=-1)
        for campo in ("humedad_suelo_min", "temperatura_max", "luz_lux_min"):
            for invalido in ("10", None, True):
                with self.subTest(campo=campo, valor=invalido):
                    with self.assertRaises(PlantaInvalidaError):
                        crear_planta(**{campo: invalido})

    def test_los_errores_de_planta_son_de_validacion(self) -> None:
        with self.assertRaises(ValidationError):
            crear_planta(slug="X")
        with self.assertRaises(ValidationError):
            crear_planta(id=0)


class IdentificadoresTests(unittest.TestCase):
    def test_es_entero_positivo(self) -> None:
        self.assertTrue(es_entero_positivo(1))
        for valor in (0, -3, True, "2", 2.0, None):
            with self.subTest(valor=valor):
                self.assertFalse(es_entero_positivo(valor))
