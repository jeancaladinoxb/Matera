import { ResultadoAplicacion } from "../../resultado-aplicacion";

export interface SolicitudInicioSesion {
  readonly correo: string;
  readonly contrasena: string;
}

export interface IniciarSesionPort {
  iniciarSesion(
    solicitud: SolicitudInicioSesion,
  ): Promise<ResultadoAplicacion<void>>;
}
