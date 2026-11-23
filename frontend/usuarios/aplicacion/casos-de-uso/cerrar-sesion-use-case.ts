import { CerrarSesionPort } from "../puertos/entrada/cerrar-sesion-port";
import { SessionPort } from "../puertos/salida/session-port";

export class CerrarSesionUseCase implements CerrarSesionPort {
  constructor(private readonly session: SessionPort) {}

  cerrarSesion() {
    return this.session.cerrarSesion();
  }
}
