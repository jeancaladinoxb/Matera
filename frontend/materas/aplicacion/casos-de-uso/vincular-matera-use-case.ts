import { CodigoDeVinculacion } from "../../dominio/codigo-de-vinculacion";
import { DireccionMac } from "../../dominio/direccion-mac";
import { ErrorValidacionMatera } from "../../dominio/errores-dominio";
import {
  ResultadoAplicacion,
  fallo,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  VincularMateraPort,
  SolicitudVincularMatera,
} from "../puertos/entrada/vincular-matera-port";
import { MateraRepositoryPort } from "../puertos/salida/matera-repository-port";

export class VincularMateraUseCase implements VincularMateraPort {
  constructor(private readonly repository: MateraRepositoryPort) {}

  async vincular(
    solicitud: SolicitudVincularMatera,
  ): Promise<ResultadoAplicacion<void>> {
    let mac: DireccionMac;
    let codigo: CodigoDeVinculacion;

    try {
      mac = new DireccionMac(solicitud.mac);
      codigo = new CodigoDeVinculacion(solicitud.codigo);
    } catch (error) {
      if (error instanceof ErrorValidacionMatera) {
        return fallo<void>({
          tipo: "validacion",
          mensaje: error.message,
        });
      }
      throw error;
    }

    try {
      return await this.repository.vincular(
        mac.valor,
        codigo.obtenerValor(),
      );
    } catch {
      return fallo<void>({ tipo: "desconocido" });
    }
  }
}
