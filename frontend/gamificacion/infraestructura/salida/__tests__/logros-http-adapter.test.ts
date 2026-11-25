import { describe, expect, it, vi } from "vitest";

import {
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../../usuarios/infraestructura/salida/cliente-http";
import { LogrosHttpAdapter } from "../logros-http-adapter";

function respuesta(estado: number, cuerpo: unknown = undefined): ResultadoHttp {
  return { tipo: "respuesta", estado, cuerpo };
}

const cuerpoValido = {
  puntos: 10,
  nivel: { numero: 1, nombre: "Semilla", puntos_minimos: 0 },
  siguiente_nivel: { numero: 2, nombre: "Brote", puntos_minimos: 20 },
  logros: [
    {
      codigo: "primer_brote",
      nombre: "Primer brote",
      descripcion: "Vincula tu primera matera.",
      icono: "🌱",
      puntos: 10,
      progreso: 1,
      meta: 1,
      desbloqueado: true,
      fecha_desbloqueo: "2026-11-01T15:30:00+00:00",
    },
  ],
};

function adapterCon(resultado: ResultadoHttp) {
  const get = vi.fn<ClienteHttpPort["get"]>().mockResolvedValue(resultado);
  const post = vi.fn<ClienteHttpPort["post"]>();
  return { adapter: new LogrosHttpAdapter({ get, post }), get };
}

describe("LogrosHttpAdapter", () => {
  it("consulta /logros y mapea el contrato a camelCase", async () => {
    const { adapter, get } = adapterCon(respuesta(200, cuerpoValido));

    const resultado = await adapter.consultarLogros();

    expect(get).toHaveBeenCalledWith("logros");
    expect(resultado).toEqual({
      estado: "exito",
      valor: {
        puntos: 10,
        nivel: { numero: 1, nombre: "Semilla", puntosMinimos: 0 },
        siguienteNivel: { numero: 2, nombre: "Brote", puntosMinimos: 20 },
        logros: [
          {
            codigo: "primer_brote",
            nombre: "Primer brote",
            descripcion: "Vincula tu primera matera.",
            icono: "🌱",
            puntos: 10,
            progreso: 1,
            meta: 1,
            desbloqueado: true,
            fechaDesbloqueo: new Date("2026-11-01T15:30:00Z"),
          },
        ],
      },
    });
  });

  it("acepta siguiente_nivel nulo en el nivel máximo", async () => {
    const { adapter } = adapterCon(
      respuesta(200, { ...cuerpoValido, siguiente_nivel: null }),
    );

    const resultado = await adapter.consultarLogros();

    expect(resultado.estado).toBe("exito");
  });

  it.each([
    [respuesta(401), "sesion_vencida"],
    [respuesta(500), "desconocido"],
    [respuesta(200, { puntos: "10" }), "desconocido"],
    [respuesta(200, { ...cuerpoValido, logros: [{ codigo: 1 }] }), "desconocido"],
    [{ tipo: "fallo", motivo: "conexion" } as ResultadoHttp, "conexion"],
  ])("traduce %o a %s", async (http, tipo) => {
    const { adapter } = adapterCon(http);

    const resultado = await adapter.consultarLogros();

    expect(resultado).toEqual({ estado: "error", error: { tipo } });
  });
});
