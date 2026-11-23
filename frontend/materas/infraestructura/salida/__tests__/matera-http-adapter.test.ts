import { describe, expect, it, vi } from "vitest";

import {
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../../usuarios/infraestructura/salida/cliente-http";
import { MateraHttpAdapter } from "../matera-http-adapter";

function respuesta(
  estado: number,
  cuerpo: unknown = undefined,
): ResultadoHttp {
  return { tipo: "respuesta", estado, cuerpo };
}

describe("MateraHttpAdapter", () => {
  it("envía MAC normalizada y código normalizado", async () => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(respuesta(200));
    const get = vi.fn<ClienteHttpPort["get"]>();
    const adapter = new MateraHttpAdapter({ post, get });

    const resultado = await adapter.vincular(
      "246F28AB1234",
      "9f3a1c7e0b52",
    );

    expect(resultado).toEqual({ estado: "exito", valor: undefined });
    expect(post).toHaveBeenCalledWith("materas/vincular", {
      mac: "246F28AB1234",
      codigo: "9f3a1c7e0b52",
    });
  });

  it.each([
    [400, "validacion"],
    [401, "sesion_vencida"],
    [404, "matera_codigo_invalido"],
    [409, "matera_ya_vinculada"],
    [500, "desconocido"],
  ])("traduce el estado HTTP %i", async (estado, tipo) => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(respuesta(estado as number));
    const get = vi.fn<ClienteHttpPort["get"]>();
    const adapter = new MateraHttpAdapter({ post, get });

    const resultado = await adapter.vincular(
      "246F28AB1234",
      "9f3a1c7e0b52",
    );

    expect(resultado.estado).toBe("error");
    if (resultado.estado === "error") {
      expect(resultado.error.tipo).toBe(tipo);
    }
  });

  it("traduce timeout y red caída a conexión", async () => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue({ tipo: "fallo", motivo: "conexion" });
    const get = vi.fn<ClienteHttpPort["get"]>();
    const adapter = new MateraHttpAdapter({ post, get });

    const resultado = await adapter.vincular(
      "246F28AB1234",
      "9f3a1c7e0b52",
    );

    expect(resultado).toEqual({
      estado: "error",
      error: { tipo: "conexion" },
    });
  });

  it("consulta si el usuario tiene una matera vinculada", async () => {
    const get = vi
      .fn<ClienteHttpPort["get"]>()
      .mockResolvedValue(
        respuesta(200, {
          vinculada: true,
          mac: "246F28AB1234",
        }),
      );
    const post = vi.fn<ClienteHttpPort["post"]>();
    const adapter = new MateraHttpAdapter({ post, get });

    const resultado = await adapter.consultarMateraDelUsuario();

    expect(resultado).toEqual({
      estado: "exito",
      valor: { vinculada: true, mac: "246F28AB1234" },
    });
    expect(get).toHaveBeenCalledWith("materas/mias");
  });

  it("consulta una respuesta sin matera vinculada", async () => {
    const get = vi
      .fn<ClienteHttpPort["get"]>()
      .mockResolvedValue(
        respuesta(200, { vinculada: false, mac: null }),
      );
    const post = vi.fn<ClienteHttpPort["post"]>();
    const adapter = new MateraHttpAdapter({ post, get });

    const resultado = await adapter.consultarMateraDelUsuario();

    expect(resultado).toEqual({
      estado: "exito",
      valor: { vinculada: false },
    });
  });
});
