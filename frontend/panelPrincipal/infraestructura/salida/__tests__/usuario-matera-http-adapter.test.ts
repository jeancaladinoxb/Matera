import { describe, expect, it, vi } from "vitest";

import {
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../../usuarios/infraestructura/salida/cliente-http";
import { UsuarioMateraHttpAdapter } from "../usuario-matera-http-adapter";

function respuesta(estado: number, cuerpo: unknown = undefined): ResultadoHttp {
  return { tipo: "respuesta", estado, cuerpo };
}

const cuerpoValido = {
  usuario: {
    usuario_id: 7,
    nombre: "Ana",
    nickname: "anap",
  },
  materas: [
    {
      matera_id: 12,
      dispositivo_id: 12,
      planta_id: null,
      mac: "E072A1D55B18",
    },
  ],
};

describe("UsuarioMateraHttpAdapter", () => {
  it("consulta /panel una sola vez y mapea el contrato a camelCase", async () => {
    const get = vi.fn<ClienteHttpPort["get"]>().mockResolvedValue(
      respuesta(200, cuerpoValido),
    );
    const post = vi.fn<ClienteHttpPort["post"]>();
    const adapter = new UsuarioMateraHttpAdapter({ get, post });

    const resultado = await adapter.consultarPanel();

    expect(resultado).toEqual({
      estado: "exito",
      valor: {
        usuario: { usuarioId: 7, nombre: "Ana", nickname: "anap" },
        materas: [
          {
            materaId: 12,
            dispositivoId: 12,
            plantaId: null,
            mac: "E072A1D55B18",
          },
        ],
      },
    });
    expect(get).toHaveBeenCalledExactlyOnceWith("panel");
    expect(post).not.toHaveBeenCalled();
  });

  it("conserva una lista vacía como resultado válido", async () => {
    const get = vi.fn<ClienteHttpPort["get"]>().mockResolvedValue(
      respuesta(200, { ...cuerpoValido, materas: [] }),
    );
    const adapter = new UsuarioMateraHttpAdapter({
      get,
      post: vi.fn<ClienteHttpPort["post"]>(),
    });

    const resultado = await adapter.consultarPanel();

    expect(resultado).toEqual({
      estado: "exito",
      valor: {
        usuario: { usuarioId: 7, nombre: "Ana", nickname: "anap" },
        materas: [],
      },
    });
  });

  it("traduce 401 y respuestas 5xx", async () => {
    const get = vi
      .fn<ClienteHttpPort["get"]>()
      .mockResolvedValueOnce(respuesta(401))
      .mockResolvedValueOnce(respuesta(503));
    const adapter = new UsuarioMateraHttpAdapter({
      get,
      post: vi.fn<ClienteHttpPort["post"]>(),
    });

    const sesion = await adapter.consultarPanel();
    const servidor = await adapter.consultarPanel();

    expect(sesion).toEqual({
      estado: "error",
      error: { tipo: "sesion_vencida" },
    });
    expect(servidor).toEqual({
      estado: "error",
      error: { tipo: "desconocido" },
    });
  });

  it("traduce fallos de red y rechaza respuestas mal formadas", async () => {
    const get = vi
      .fn<ClienteHttpPort["get"]>()
      .mockResolvedValueOnce({ tipo: "fallo", motivo: "conexion" })
      .mockResolvedValueOnce(respuesta(200, { usuario: {}, materas: [] }));
    const adapter = new UsuarioMateraHttpAdapter({
      get,
      post: vi.fn<ClienteHttpPort["post"]>(),
    });

    const red = await adapter.consultarPanel();
    const contrato = await adapter.consultarPanel();

    expect(red).toEqual({
      estado: "error",
      error: { tipo: "conexion" },
    });
    expect(contrato).toEqual({
      estado: "error",
      error: { tipo: "desconocido" },
    });
  });
});
