import { RegistrarUsuarioUseCase } from "../../aplicacion/casos-de-uso/registrar-usuario-use-case";
import { IniciarSesionUseCase } from "../../aplicacion/casos-de-uso/iniciar-sesion-use-case";
import { CerrarSesionUseCase } from "../../aplicacion/casos-de-uso/cerrar-sesion-use-case";
import { RegistroHttpAdapter } from "../salida/registro-http-adapter";
import { SessionHttpAdapter } from "../salida/session-http-adapter";
import { ClienteHttp } from "../salida/cliente-http";

export function crearComposicionUsuarios() {
  const clienteHttp = new ClienteHttp();
  const registroHttp = new RegistroHttpAdapter(clienteHttp);
  const sessionHttp = new SessionHttpAdapter(clienteHttp);

  return {
    registrarUsuario: new RegistrarUsuarioUseCase(registroHttp),
    iniciarSesion: new IniciarSesionUseCase(sessionHttp),
    cerrarSesion: new CerrarSesionUseCase(sessionHttp),
    sessionHttp,
  };
}

export type ComposicionUsuarios = ReturnType<typeof crearComposicionUsuarios>;
