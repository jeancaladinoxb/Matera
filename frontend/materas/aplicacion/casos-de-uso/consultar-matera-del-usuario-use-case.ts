import {
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  ConsultarMateraDelUsuarioPort,
  MateraDelUsuario,
} from "../puertos/entrada/consultar-matera-del-usuario-port";
import { MateraRepositoryPort } from "../puertos/salida/matera-repository-port";

export class ConsultarMateraDelUsuarioUseCase
  implements ConsultarMateraDelUsuarioPort
{
  constructor(private readonly repository: MateraRepositoryPort) {}

  consultarMateraDelUsuario(): Promise<
    ResultadoAplicacion<MateraDelUsuario>
  > {
    return this.repository.consultarMateraDelUsuario();
  }
}
