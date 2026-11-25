import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { DatosPlanta } from "../../../dominio/planta";

export interface PlantaRepositoryPort {
  listarPlantas(): Promise<ResultadoAplicacion<readonly DatosPlanta[]>>;

  vincular(
    materaId: number,
    plantaId: number,
  ): Promise<ResultadoAplicacion<void>>;
}
