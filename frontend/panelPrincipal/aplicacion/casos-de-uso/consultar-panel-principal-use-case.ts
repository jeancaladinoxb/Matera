import { fallo, exito, ResultadoAplicacion } from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  ErrorValidacionPanelPrincipal,
} from "../../dominio/errores-dominio";
import { Matera } from "../../dominio/matera";
import { PanelPrincipal } from "../../dominio/panel-principal";
import { Usuario } from "../../dominio/usuario";
import { ConsultarPanelPrincipalPort } from "../puertos/entrada/consultar-panel-principal-port";
import { PanelRepositoryPort } from "../puertos/salida/panel-repository-port";

export class ConsultarPanelPrincipalUseCase
  implements ConsultarPanelPrincipalPort
{
  constructor(private readonly repository: PanelRepositoryPort) {}

  async consultarPanelPrincipal(): Promise<
    ResultadoAplicacion<PanelPrincipal>
  > {
    const resultado = await this.repository.consultarPanel();
    if (resultado.estado === "error") {
      return fallo(resultado.error);
    }

    try {
      const usuario = new Usuario(resultado.valor.usuario);
      const materas = resultado.valor.materas.map(
        (datosMatera) => new Matera(datosMatera),
      );
      return exito(new PanelPrincipal(usuario, materas));
    } catch (error) {
      if (error instanceof ErrorValidacionPanelPrincipal) {
        return fallo({ tipo: "desconocido" });
      }
      throw error;
    }
  }
}
