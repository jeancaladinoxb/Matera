import {
  ResultadoAplicacion,
} from "../../../../usuarios/aplicacion/resultado-aplicacion";

export interface SolicitudVincularMatera {
  readonly mac: string;
  readonly codigo: string;
}

export interface VincularMateraPort {
  vincular(
    solicitud: SolicitudVincularMatera,
  ): Promise<ResultadoAplicacion<void>>;
}
