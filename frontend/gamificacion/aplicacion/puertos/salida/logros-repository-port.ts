import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { DatosLogro } from "../../../dominio/logro";
import { Nivel } from "../../../dominio/perfil-gamificacion";

export interface DatosPerfilGamificacion {
  readonly puntos: number;
  readonly nivel: Nivel;
  readonly siguienteNivel: Nivel | null;
  readonly logros: readonly DatosLogro[];
}

export interface LogrosRepositoryPort {
  consultarLogros(): Promise<ResultadoAplicacion<DatosPerfilGamificacion>>;
}
