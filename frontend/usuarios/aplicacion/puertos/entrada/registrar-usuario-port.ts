import { ResultadoAplicacion } from "../../resultado-aplicacion";

export interface SolicitudRegistro {
  readonly nombre: string;
  readonly apellido: string;
  readonly nickname: string;
  readonly correo: string;
  readonly contrasena: string;
}

export interface RegistrarUsuarioPort {
  registrarUsuario(
    solicitud: SolicitudRegistro,
  ): Promise<ResultadoAplicacion<void>>;
}
