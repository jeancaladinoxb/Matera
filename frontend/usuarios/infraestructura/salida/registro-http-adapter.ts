import { Usuario } from "../../dominio/usuario";
import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../aplicacion/resultado-aplicacion";
import { UsuarioRepositoryPort } from "../../aplicacion/puertos/salida/usuario-repository-port";
import { ClienteHttp, ClienteHttpPort, ResultadoHttp } from "./cliente-http";

export class RegistroHttpAdapter implements UsuarioRepositoryPort {
  constructor(private readonly clienteHttp: ClienteHttpPort = new ClienteHttp()) {}

  async registrar(usuario: Usuario): Promise<ResultadoAplicacion<void>> {
    const respuesta = await this.clienteHttp.post("registro", {
      nombre: usuario.nombre,
      apellido: usuario.apellido,
      nickname: usuario.nickname,
      correo: usuario.correo.valor,
      contrasena: usuario.contrasena.valor,
    });

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo({ tipo: "conexion" })
        : fallo({ tipo: "desconocido" });
    }

    if (respuesta.estado === 201) {
      return exito(undefined);
    }

    if (respuesta.estado === 400) {
      return fallo({
        tipo: "validacion",
        mensaje: obtenerMensaje(respuesta) ?? "Revisa los datos ingresados.",
      });
    }

    return fallo({ tipo: "desconocido" });
  }
}

function obtenerMensaje(
  respuesta: Extract<ResultadoHttp, { tipo: "respuesta" }>,
): string | undefined {
  const cuerpo = esObjeto(respuesta.cuerpo) ? respuesta.cuerpo : undefined;
  return typeof cuerpo?.error === "string" ? cuerpo.error : undefined;
}

function esObjeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === "object" && valor !== null
    && !Array.isArray(valor);
}
