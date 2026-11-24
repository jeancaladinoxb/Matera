import { MateraPanelInvalidaError } from "./errores-dominio";

export interface DatosMatera {
  readonly materaId: number;
  readonly dispositivoId: number;
  readonly plantaId: number | null;
  readonly mac: string;
}

export class Matera {
  readonly materaId: number;
  readonly dispositivoId: number;
  readonly plantaId: number | null;
  readonly mac: string;

  constructor(datos: DatosMatera) {
    if (
      !Number.isSafeInteger(datos.materaId) ||
      datos.materaId <= 0 ||
      !Number.isSafeInteger(datos.dispositivoId) ||
      datos.dispositivoId <= 0 ||
      (datos.plantaId !== null &&
        (!Number.isSafeInteger(datos.plantaId) || datos.plantaId <= 0)) ||
      typeof datos.mac !== "string" ||
      datos.mac.trim().length === 0
    ) {
      throw new MateraPanelInvalidaError();
    }

    this.materaId = datos.materaId;
    this.dispositivoId = datos.dispositivoId;
    this.plantaId = datos.plantaId;
    this.mac = datos.mac;
  }

  get sugerirVincularPlanta(): boolean {
    return this.plantaId === null;
  }
}
