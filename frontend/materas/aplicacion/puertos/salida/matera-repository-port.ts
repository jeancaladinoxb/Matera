import {
  ResultadoAplicacion,
} from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { MateraDelUsuario } from "../entrada/consultar-matera-del-usuario-port";

export interface MateraRepositoryPort {
  vincular(
    mac: string,
    codigo: string,
  ): Promise<ResultadoAplicacion<void>>;

  consultarMateraDelUsuario(): Promise<
    ResultadoAplicacion<MateraDelUsuario>
  >;
}
