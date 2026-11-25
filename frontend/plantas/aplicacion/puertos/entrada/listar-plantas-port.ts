import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { Planta } from "../../../dominio/planta";

export interface ListarPlantasPort {
  listarPlantas(): Promise<ResultadoAplicacion<readonly Planta[]>>;
}
