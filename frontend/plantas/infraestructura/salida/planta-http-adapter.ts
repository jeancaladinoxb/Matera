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
import { PlantaRepositoryPort } from "../../aplicacion/puertos/salida/planta-repository-port";
import { DatosPlanta } from "../../dominio/planta";

export class PlantaHttpAdapter implements PlantaRepositoryPort {
  constructor(
    private readonly clienteHttp: ClienteHttpPort = new ClienteHttp(),
  ) {}

  async listarPlantas(): Promise<
    ResultadoAplicacion<readonly DatosPlanta[]>
  > {
    const respuesta = await this.clienteHttp.get("plantas");

    if (respuesta.tipo === "fallo") {
      return fallaDeRed(respuesta);
    }
    if (respuesta.estado === 401) {
      return fallo({ tipo: "sesion_vencida" });
    }
    if (respuesta.estado !== 200) {
      return fallo({ tipo: "desconocido" });
    }

    const plantas = esObjeto(respuesta.cuerpo)
      ? respuesta.cuerpo.plantas
      : undefined;
    if (!Array.isArray(plantas)) {
      return fallo({ tipo: "desconocido" });
    }

    const datos: DatosPlanta[] = [];
    for (const planta of plantas) {
      const mapeada = mapearPlanta(planta);
      if (!mapeada) {
        return fallo({ tipo: "desconocido" });
      }
      datos.push(mapeada);
    }
    return exito(datos);
  }

  async vincular(
    materaId: number,
    plantaId: number,
  ): Promise<ResultadoAplicacion<void>> {
    const respuesta = await this.clienteHttp.post(
      `materas/${materaId}/planta`,
      { planta_id: plantaId },
    );

    if (respuesta.tipo === "fallo") {
      return fallaDeRed<void>(respuesta);
    }

    switch (respuesta.estado) {
      case 200:
        return exito(undefined);
      case 400:
        return fallo<void>({
          tipo: "validacion",
          mensaje: "No pudimos validar tu selección. Inténtalo de nuevo.",
        });
      case 401:
        return fallo<void>({ tipo: "sesion_vencida" });
      case 404:
        return fallo<void>({ tipo: "no_encontrado" });
      default:
        return fallo<void>({ tipo: "desconocido" });
    }
  }
}

function fallaDeRed<T>(
  respuesta: Extract<ResultadoHttp, { tipo: "fallo" }>,
): ResultadoAplicacion<T> {
  return respuesta.motivo === "conexion"
    ? fallo<T>({ tipo: "conexion" })
    : fallo<T>({ tipo: "desconocido" });
}

function mapearPlanta(valor: unknown): DatosPlanta | undefined {
  if (
    !esObjeto(valor) ||
    typeof valor.id !== "number" ||
    typeof valor.slug !== "string" ||
    typeof valor.nombre_comun !== "string" ||
    typeof valor.nombre_cientifico !== "string" ||
    typeof valor.luz !== "string" ||
    typeof valor.riego !== "string"
  ) {
    return undefined;
  }

  return {
    id: valor.id,
    slug: valor.slug,
    nombreComun: valor.nombre_comun,
    nombreCientifico: valor.nombre_cientifico,
    luz: valor.luz,
    riego: valor.riego,
  };
}

function esObjeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === "object" && valor !== null && !Array.isArray(valor);
}
