import { PerfilGamificacionInvalidoError } from "./errores-dominio";
import { Logro } from "./logro";

export interface Nivel {
  readonly numero: number;
  readonly nombre: string;
  readonly puntosMinimos: number;
}

function esNivelValido(nivel: Nivel): boolean {
  return (
    Number.isSafeInteger(nivel.numero) &&
    nivel.numero > 0 &&
    typeof nivel.nombre === "string" &&
    nivel.nombre.trim() !== "" &&
    Number.isSafeInteger(nivel.puntosMinimos) &&
    nivel.puntosMinimos >= 0
  );
}

export class PerfilGamificacion {
  readonly puntos: number;
  readonly nivel: Nivel;
  readonly siguienteNivel: Nivel | null;
  readonly logros: readonly Logro[];

  constructor(
    puntos: number,
    nivel: Nivel,
    siguienteNivel: Nivel | null,
    logros: readonly Logro[],
  ) {
    if (
      !Number.isSafeInteger(puntos) ||
      puntos < 0 ||
      !esNivelValido(nivel) ||
      (siguienteNivel !== null &&
        (!esNivelValido(siguienteNivel) ||
          siguienteNivel.puntosMinimos <= nivel.puntosMinimos)) ||
      !Array.isArray(logros) ||
      logros.some((logro) => !(logro instanceof Logro))
    ) {
      throw new PerfilGamificacionInvalidoError();
    }

    this.puntos = puntos;
    this.nivel = nivel;
    this.siguienteNivel = siguienteNivel;
    this.logros = Object.freeze([...logros]);
  }

  get logrosDesbloqueados(): number {
    return this.logros.filter((logro) => logro.desbloqueado).length;
  }

  get puntosParaSiguienteNivel(): number {
    if (this.siguienteNivel === null) return 0;
    return Math.max(0, this.siguienteNivel.puntosMinimos - this.puntos);
  }

  /** Avance dentro del nivel actual, de 0 a 100. */
  get porcentajeNivel(): number {
    if (this.siguienteNivel === null) return 100;
    const rango = this.siguienteNivel.puntosMinimos - this.nivel.puntosMinimos;
    const avance = this.puntos - this.nivel.puntosMinimos;
    return Math.min(100, Math.max(0, Math.round((avance / rango) * 100)));
  }
}
