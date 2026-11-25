import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import {
  ClienteHttp,
  ClienteHttpPort,
} from "../../../usuarios/infraestructura/salida/cliente-http";
import {
  DatosPerfilGamificacion,
  LogrosRepositoryPort,
} from "../../aplicacion/puertos/salida/logros-repository-port";
import { DatosLogro } from "../../dominio/logro";
import { Nivel } from "../../dominio/perfil-gamificacion";

export class LogrosHttpAdapter implements LogrosRepositoryPort {
  constructor(
    private readonly clienteHttp: ClienteHttpPort = new ClienteHttp(),
  ) {}

  async consultarLogros(): Promise<
    ResultadoAplicacion<DatosPerfilGamificacion>
  > {
    const respuesta = await this.clienteHttp.get("logros");

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

    const perfil = mapearPerfil(respuesta.cuerpo);
    return perfil ? exito(perfil) : fallo({ tipo: "desconocido" });
  }
}

function mapearPerfil(cuerpo: unknown): DatosPerfilGamificacion | undefined {
  if (!esObjeto(cuerpo) || typeof cuerpo.puntos !== "number") {
    return undefined;
  }
  const nivel = mapearNivel(cuerpo.nivel);
  const siguienteNivel =
    cuerpo.siguiente_nivel === null ? null : mapearNivel(cuerpo.siguiente_nivel);
  if (!nivel || siguienteNivel === undefined || !Array.isArray(cuerpo.logros)) {
    return undefined;
  }

  const logros: DatosLogro[] = [];
  for (const valor of cuerpo.logros) {
    const logro = mapearLogro(valor);
    if (!logro) return undefined;
    logros.push(logro);
  }

  return { puntos: cuerpo.puntos, nivel, siguienteNivel, logros };
}

function mapearNivel(valor: unknown): Nivel | undefined {
  if (
    !esObjeto(valor) ||
    typeof valor.numero !== "number" ||
    typeof valor.nombre !== "string" ||
    typeof valor.puntos_minimos !== "number"
  ) {
    return undefined;
  }
  return {
    numero: valor.numero,
    nombre: valor.nombre,
    puntosMinimos: valor.puntos_minimos,
  };
}

function mapearLogro(valor: unknown): DatosLogro | undefined {
  if (
    !esObjeto(valor) ||
    typeof valor.codigo !== "string" ||
    typeof valor.nombre !== "string" ||
    typeof valor.descripcion !== "string" ||
    typeof valor.icono !== "string" ||
    typeof valor.puntos !== "number" ||
    typeof valor.progreso !== "number" ||
    typeof valor.meta !== "number" ||
    typeof valor.desbloqueado !== "boolean" ||
    (valor.fecha_desbloqueo !== null && typeof valor.fecha_desbloqueo !== "string")
  ) {
    return undefined;
  }

  return {
    codigo: valor.codigo,
    nombre: valor.nombre,
    descripcion: valor.descripcion,
    icono: valor.icono,
    puntos: valor.puntos,
    progreso: valor.progreso,
    meta: valor.meta,
    desbloqueado: valor.desbloqueado,
    fechaDesbloqueo:
      valor.fecha_desbloqueo === null ? null : new Date(valor.fecha_desbloqueo),
  };
}

function esObjeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === "object" && valor !== null && !Array.isArray(valor);
}
