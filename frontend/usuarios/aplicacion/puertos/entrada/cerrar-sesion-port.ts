import { ResultadoAplicacion } from "../../resultado-aplicacion";

export interface CerrarSesionPort {
  cerrarSesion(): Promise<ResultadoAplicacion<void>>;
}
