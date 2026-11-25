import { PlantaInvalidaError } from "./errores-dominio";

export const NIVELES_LUZ = ["baja", "indirecta", "directa"] as const;
export const NIVELES_RIEGO = ["bajo", "moderado", "alto"] as const;

export type NivelLuz = (typeof NIVELES_LUZ)[number];
export type NivelRiego = (typeof NIVELES_RIEGO)[number];

export interface DatosPlanta {
  readonly id: number;
  readonly slug: string;
  readonly nombreComun: string;
  readonly nombreCientifico: string;
  readonly luz: string;
  readonly riego: string;
}

const SLUG = /^[a-z0-9_]+$/;

export function esIdentificadorPositivo(valor: unknown): valor is number {
  return typeof valor === "number" && Number.isSafeInteger(valor) && valor > 0;
}

function esTextoNoVacio(valor: unknown): valor is string {
  return typeof valor === "string" && valor.trim().length > 0;
}

function esNivelLuz(valor: unknown): valor is NivelLuz {
  return NIVELES_LUZ.some((nivel) => nivel === valor);
}

function esNivelRiego(valor: unknown): valor is NivelRiego {
  return NIVELES_RIEGO.some((nivel) => nivel === valor);
}

export class Planta {
  readonly id: number;
  readonly slug: string;
  readonly nombreComun: string;
  readonly nombreCientifico: string;
  readonly luz: NivelLuz;
  readonly riego: NivelRiego;

  constructor(datos: DatosPlanta) {
    if (
      !esIdentificadorPositivo(datos.id) ||
      typeof datos.slug !== "string" ||
      !SLUG.test(datos.slug) ||
      !esTextoNoVacio(datos.nombreComun) ||
      !esTextoNoVacio(datos.nombreCientifico) ||
      !esNivelLuz(datos.luz) ||
      !esNivelRiego(datos.riego)
    ) {
      throw new PlantaInvalidaError();
    }

    this.id = datos.id;
    this.slug = datos.slug;
    this.nombreComun = datos.nombreComun;
    this.nombreCientifico = datos.nombreCientifico;
    this.luz = datos.luz;
    this.riego = datos.riego;
  }
}
