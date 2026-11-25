import {
  ResultadoAplicacion,
  exito,
  fallo,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { ErrorValidacionPlanta } from "../../dominio/errores-dominio";
import { Planta } from "../../dominio/planta";
import { ListarPlantasPort } from "../puertos/entrada/listar-plantas-port";
import { PlantaRepositoryPort } from "../puertos/salida/planta-repository-port";

export class ListarPlantasUseCase implements ListarPlantasPort {
  constructor(private readonly repository: PlantaRepositoryPort) {}

  async listarPlantas(): Promise<ResultadoAplicacion<readonly Planta[]>> {
    let resultado: Awaited<ReturnType<PlantaRepositoryPort["listarPlantas"]>>;
    try {
      resultado = await this.repository.listarPlantas();
    } catch {
      return fallo({ tipo: "desconocido" });
    }
    if (resultado.estado === "error") {
      return fallo(resultado.error);
    }

    try {
      return exito(resultado.valor.map((datos) => new Planta(datos)));
    } catch (error) {
      if (error instanceof ErrorValidacionPlanta) {
        return fallo({ tipo: "desconocido" });
      }
      throw error;
    }
  }
}
