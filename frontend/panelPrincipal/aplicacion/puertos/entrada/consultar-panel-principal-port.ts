import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";
import { PanelPrincipal } from "../../../dominio/panel-principal";

export interface ConsultarPanelPrincipalPort {
  consultarPanelPrincipal(): Promise<ResultadoAplicacion<PanelPrincipal>>;
}
