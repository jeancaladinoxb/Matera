import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { MateraRepositoryPort } from "../../aplicacion/puertos/salida/matera-repository-port";
import { MateraDelUsuario } from "../../aplicacion/puertos/entrada/consultar-matera-del-usuario-port";
import {
  ClienteHttp,
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../usuarios/infraestructura/salida/cliente-http";

export class MateraHttpAdapter implements MateraRepositoryPort {
  constructor(
    private readonly clienteHttp: ClienteHttpPort = new ClienteHttp(),
  ) {}

  async vincular(
    mac: string,
    codigo: string,
  ): Promise<ResultadoAplicacion<void>> {
    const respuesta = await this.clienteHttp.post("materas/vincular", {
      mac,
      codigo,
    });

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo<void>({ tipo: "conexion" })
        : fallo<void>({ tipo: "desconocido" });
    }

    if (respuesta.estado === 200) {
      return exito(undefined);
    }
    if (respuesta.estado === 400) {
      return fallo<void>({
        tipo: "validacion",
        mensaje: "Revisa el formato de la MAC y del código.",
      });
    }
    if (respuesta.estado === 401) {
      return fallo<void>({ tipo: "sesion_vencida" });
    }
    if (respuesta.estado === 404) {
      return fallo<void>({ tipo: "matera_codigo_invalido" });
    }
    if (respuesta.estado === 409) {
      return fallo<void>({ tipo: "matera_ya_vinculada" });
    }
    return fallo<void>({ tipo: "desconocido" });
  }

  async consultarMateraDelUsuario(): Promise<
    ResultadoAplicacion<MateraDelUsuario>
  > {
    const respuesta = await this.clienteHttp.get("materas/mias");

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo<MateraDelUsuario>({ tipo: "conexion" })
        : fallo<MateraDelUsuario>({ tipo: "desconocido" });
    }

    if (respuesta.estado === 401) {
      return fallo<MateraDelUsuario>({ tipo: "sesion_vencida" });
    }
    if (respuesta.estado !== 200) {
      return fallo<MateraDelUsuario>({ tipo: "desconocido" });
    }

    const cuerpo = esObjeto(respuesta.cuerpo) ? respuesta.cuerpo : undefined;
    if (
      !cuerpo ||
      typeof cuerpo.vinculada !== "boolean"
    ) {
      return fallo<MateraDelUsuario>({ tipo: "desconocido" });
    }

    if (!cuerpo.vinculada) {
      return exito<MateraDelUsuario>({
        vinculada: false,
      });
    }

    if (typeof cuerpo.mac === "string") {
      return exito<MateraDelUsuario>({
        vinculada: true,
        mac: cuerpo.mac,
      });
    }

    return fallo<MateraDelUsuario>({ tipo: "desconocido" });
  }
}

function esObjeto(valor: unknown): valor is Record<string, unknown> {
  return (
    typeof valor === "object" &&
    valor !== null &&
    !Array.isArray(valor)
  );
}
