import {
  ResultadoAplicacion,
  fallo,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  IdentificadorMateraInvalidoError,
  IdentificadorPlantaInvalidoError,
} from "../../dominio/errores-dominio";
import { esIdentificadorPositivo } from "../../dominio/planta";
import {
  SolicitudVincularPlanta,
  VincularPlantaPort,
} from "../puertos/entrada/vincular-planta-port";
import { PlantaRepositoryPort } from "../puertos/salida/planta-repository-port";

export class VincularPlantaUseCase implements VincularPlantaPort {
  constructor(private readonly repository: PlantaRepositoryPort) {}

  async vincularPlanta(
    solicitud: SolicitudVincularPlanta,
  ): Promise<ResultadoAplicacion<void>> {
    if (!esIdentificadorPositivo(solicitud.materaId)) {
      return fallo<void>({
        tipo: "validacion",
        mensaje: new IdentificadorMateraInvalidoError().message,
      });
    }
    if (!esIdentificadorPositivo(solicitud.plantaId)) {
      return fallo<void>({
        tipo: "validacion",
        mensaje: new IdentificadorPlantaInvalidoError().message,
      });
    }

    try {
      return await this.repository.vincular(
        solicitud.materaId,
        solicitud.plantaId,
      );
    } catch {
      return fallo<void>({ tipo: "desconocido" });
    }
  }
}
