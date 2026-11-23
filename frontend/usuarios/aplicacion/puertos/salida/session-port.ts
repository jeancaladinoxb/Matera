import { CorreoElectronico } from "../../../dominio/correo-electronico";
import { ContraseñaDeInicioSesion } from "../../../dominio/contrasena-de-inicio-sesion";
import { ResultadoAplicacion } from "../../resultado-aplicacion";

export interface SessionPort {
  iniciarSesion(
    correo: CorreoElectronico,
    contrasena: ContraseñaDeInicioSesion,
  ): Promise<ResultadoAplicacion<void>>;

  cerrarSesion(): Promise<ResultadoAplicacion<void>>;
}
