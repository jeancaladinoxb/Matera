import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { ErrorValidacionGamificacion } from "../../dominio/errores-dominio";
import { Logro } from "../../dominio/logro";
import { PerfilGamificacion } from "../../dominio/perfil-gamificacion";
import { ConsultarLogrosPort } from "../puertos/entrada/consultar-logros-port";
import { LogrosRepositoryPort } from "../puertos/salida/logros-repository-port";

export class ConsultarLogrosUseCase implements ConsultarLogrosPort {
  constructor(private readonly repository: LogrosRepositoryPort) {}

  async consultarLogros(): Promise<ResultadoAplicacion<PerfilGamificacion>> {
    const resultado = await this.repository.consultarLogros();
    if (resultado.estado === "error") {
      return fallo(resultado.error);
    }

    try {
      const datos = resultado.valor;
      const logros = datos.logros.map((logro) => new Logro(logro));
      return exito(
        new PerfilGamificacion(
          datos.puntos,
          datos.nivel,
          datos.siguienteNivel,
          logros,
        ),
      );
    } catch (error) {
      if (error instanceof ErrorValidacionGamificacion) {
        return fallo({ tipo: "desconocido" });
      }
      throw error;
    }
  }
}
