import { CorreoElectronico } from "../../dominio/correo-electronico";
import { ContraseñaDeRegistro } from "../../dominio/contrasena-de-registro";
import { ErrorValidacionDominio } from "../../dominio/errores-dominio";
import { Usuario } from "../../dominio/usuario";
import { ResultadoAplicacion, fallo } from "../resultado-aplicacion";
import { RegistrarUsuarioPort } from "../puertos/entrada/registrar-usuario-port";
import { UsuarioRepositoryPort } from "../puertos/salida/usuario-repository-port";

export class RegistrarUsuarioUseCase implements RegistrarUsuarioPort {
  constructor(private readonly usuarioRepository: UsuarioRepositoryPort) {}

  async registrarUsuario(
    solicitud: Parameters<RegistrarUsuarioPort["registrarUsuario"]>[0],
  ): Promise<ResultadoAplicacion<void>> {
    let usuario: Usuario;

    try {
      usuario = new Usuario({
        nombre: solicitud.nombre,
        apellido: solicitud.apellido,
        nickname: solicitud.nickname,
        correo: new CorreoElectronico(solicitud.correo),
        contrasena: new ContraseñaDeRegistro(solicitud.contrasena),
      });
    } catch (error) {
      if (error instanceof ErrorValidacionDominio) {
        return fallo<void>({ tipo: "validacion", mensaje: error.message });
      }
      throw error;
    }

    return this.usuarioRepository.registrar(usuario);
  }
}
