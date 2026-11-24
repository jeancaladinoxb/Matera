import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  ClienteHttp,
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../usuarios/infraestructura/salida/cliente-http";
import {
  DatosMateraPanel,
  DatosPanelPrincipal,
  PanelRepositoryPort,
} from "../../aplicacion/puertos/salida/panel-repository-port";

export class UsuarioMateraHttpAdapter implements PanelRepositoryPort {
  constructor(
    private readonly clienteHttp: ClienteHttpPort = new ClienteHttp(),
  ) {}

  async consultarPanel(): Promise<
    ResultadoAplicacion<DatosPanelPrincipal>
  > {
    const respuesta = await this.clienteHttp.get("panel");

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo({ tipo: "conexion" })
        : fallo({ tipo: "desconocido" });
    }

    if (respuesta.estado === 401) {
      return fallo({ tipo: "sesion_vencida" });
    }
    if (respuesta.estado !== 200) {
      return fallo({ tipo: "desconocido" });
    }

    return mapearPanel(respuesta);
  }
}

function mapearPanel(
  respuesta: Extract<ResultadoHttp, { tipo: "respuesta" }>,
): ResultadoAplicacion<DatosPanelPrincipal> {
  if (!esObjeto(respuesta.cuerpo)) {
    return fallo({ tipo: "desconocido" });
  }

  const usuario = respuesta.cuerpo.usuario;
  const materas = respuesta.cuerpo.materas;
  if (
    !esObjeto(usuario) ||
    typeof usuario.usuario_id !== "number" ||
    typeof usuario.nombre !== "string" ||
    typeof usuario.nickname !== "string" ||
    !Array.isArray(materas)
  ) {
    return fallo({ tipo: "desconocido" });
  }

  const datosMateras: DatosMateraPanel[] = [];
  for (const matera of materas) {
    const datosMatera = mapearMatera(matera);
    if (!datosMatera) {
      return fallo({ tipo: "desconocido" });
    }
    datosMateras.push(datosMatera);
  }

  return exito({
    usuario: {
      usuarioId: usuario.usuario_id,
      nombre: usuario.nombre,
      nickname: usuario.nickname,
    },
    materas: datosMateras,
  });
}

function mapearMatera(valor: unknown): DatosMateraPanel | undefined {
  if (
    !esObjeto(valor) ||
    typeof valor.matera_id !== "number" ||
    typeof valor.dispositivo_id !== "number" ||
    (valor.planta_id !== null && typeof valor.planta_id !== "number") ||
    typeof valor.mac !== "string"
  ) {
    return undefined;
  }

  return {
    materaId: valor.matera_id,
    dispositivoId: valor.dispositivo_id,
    plantaId: valor.planta_id,
    mac: valor.mac,
  };
}

function esObjeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === "object" && valor !== null && !Array.isArray(valor);
}
