from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Nivel:
    numero: int
    nombre: str
    puntos_minimos: int


# Ordenados de menor a mayor. La suma de puntos de todos los logros es 120.
NIVELES: Tuple[Nivel, ...] = (
    Nivel(1, "Semilla", 0),
    Nivel(2, "Brote", 20),
    Nivel(3, "Plántula", 50),
    Nivel(4, "Jardinero", 90),
    Nivel(5, "Maestro jardinero", 120),
)


def nivel_para(puntos: int) -> Nivel:
    actual = NIVELES[0]
    for nivel in NIVELES:
        if puntos >= nivel.puntos_minimos:
            actual = nivel
    return actual


def siguiente_nivel(nivel: Nivel) -> Optional[Nivel]:
    for candidato in NIVELES:
        if candidato.numero == nivel.numero + 1:
            return candidato
    return None
