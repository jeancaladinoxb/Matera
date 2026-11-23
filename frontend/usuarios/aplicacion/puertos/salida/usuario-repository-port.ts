import { Usuario } from "../../../dominio/usuario";
import { ResultadoAplicacion } from "../../resultado-aplicacion";

export interface UsuarioRepositoryPort {
  registrar(usuario: Usuario): Promise<ResultadoAplicacion<void>>;
}
