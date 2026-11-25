import { LogroInvalidoError } from "./errores-dominio";

export interface DatosLogro {
  readonly codigo: string;
  readonly nombre: string;
  readonly descripcion: string;
  readonly icono: string;
  readonly puntos: number;
  readonly progreso: number;
  readonly meta: number;
  readonly desbloqueado: boolean;
  readonly fechaDesbloqueo: Date | null;
}

function esEnteroNoNegativo(valor: number): boolean {
  return Number.isSafeInteger(valor) && valor >= 0;
}

/**
 * Modelo de lectura: las reglas que deciden si un logro se desbloquea viven
 * en el backend. Aquí solo se valida que los datos sean coherentes para
 * mostrarlos.
 */
export class Logro {
  readonly codigo: string;
  readonly nombre: string;
  readonly descripcion: string;
  readonly icono: string;
  readonly puntos: number;
  readonly progreso: number;
  readonly meta: number;
  readonly desbloqueado: boolean;
  readonly fechaDesbloqueo: Date | null;

  constructor(datos: DatosLogro) {
    const textos = [datos.codigo, datos.nombre, datos.descripcion, datos.icono];
    if (
      textos.some((texto) => typeof texto !== "string" || texto.trim() === "") ||
      !esEnteroNoNegativo(datos.puntos) ||
      !esEnteroNoNegativo(datos.progreso) ||
      !esEnteroNoNegativo(datos.meta) ||
      datos.meta === 0 ||
      datos.progreso > datos.meta ||
      typeof datos.desbloqueado !== "boolean" ||
      datos.desbloqueado !== (datos.fechaDesbloqueo !== null) ||
      (datos.fechaDesbloqueo !== null &&
        (!(datos.fechaDesbloqueo instanceof Date) ||
          Number.isNaN(datos.fechaDesbloqueo.getTime())))
    ) {
      throw new LogroInvalidoError();
    }

    this.codigo = datos.codigo;
    this.nombre = datos.nombre;
    this.descripcion = datos.descripcion;
    this.icono = datos.icono;
    this.puntos = datos.puntos;
    this.progreso = datos.progreso;
    this.meta = datos.meta;
    this.desbloqueado = datos.desbloqueado;
    this.fechaDesbloqueo = datos.fechaDesbloqueo;
  }

  get porcentaje(): number {
    return Math.round((this.progreso / this.meta) * 100);
  }
}
