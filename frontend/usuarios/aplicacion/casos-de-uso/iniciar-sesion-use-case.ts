import { CorreoElectronico } from "../../dominio/correo-electronico";
import { ContraseñaDeInicioSesion } from "../../dominio/contrasena-de-inicio-sesion";
import { ErrorValidacionDominio } from "../../dominio/errores-dominio";
import { ResultadoAplicacion, fallo } from "../resultado-aplicacion";
import { IniciarSesionPort } from "../puertos/entrada/iniciar-sesion-port";
import { SessionPort } from "../puertos/salida/session-port";

export class IniciarSesionUseCase implements IniciarSesionPort {
  constructor(private readonly session: SessionPort) {}

  async iniciarSesion(
    solicitud: Parameters<IniciarSesionPort["iniciarSesion"]>[0],
  ): Promise<ResultadoAplicacion<void>> {
    let correo: CorreoElectronico;
    let contrasena: ContraseñaDeInicioSesion;

    try {
      correo = new CorreoElectronico(solicitud.correo);
      contrasena = new ContraseñaDeInicioSesion(solicitud.contrasena);
    } catch (error) {
      if (error instanceof ErrorValidacionDominio) {
        return fallo<void>({ tipo: "credenciales_invalidas" });
      }
      throw error;
    }

    return this.session.iniciarSesion(correo, contrasena);
  }
}
