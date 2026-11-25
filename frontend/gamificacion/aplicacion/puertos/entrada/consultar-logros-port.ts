import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { PerfilGamificacion } from "../../../dominio/perfil-gamificacion";

export interface ConsultarLogrosPort {
  consultarLogros(): Promise<ResultadoAplicacion<PerfilGamificacion>>;
}
