import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";

export interface SolicitudVincularPlanta {
  readonly materaId: number;
  readonly plantaId: number;
}

export interface VincularPlantaPort {
  vincularPlanta(
    solicitud: SolicitudVincularPlanta,
  ): Promise<ResultadoAplicacion<void>>;
}
