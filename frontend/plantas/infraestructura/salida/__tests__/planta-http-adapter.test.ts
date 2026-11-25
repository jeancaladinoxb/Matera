import { describe, expect, it, vi } from "vitest";

import {
  ClienteHttpPort,
  ResultadoHttp,
} from "../../../../usuarios/infraestructura/salida/cliente-http";
import { PlantaHttpAdapter } from "../planta-http-adapter";

function respuesta(estado: number, cuerpo: unknown = undefined): ResultadoHttp {
  return { tipo: "respuesta", estado, cuerpo };
}

function crearCliente() {
  return {
    get: vi.fn<ClienteHttpPort["get"]>(),
    post: vi.fn<ClienteHttpPort["post"]>(),
  } satisfies ClienteHttpPort;
}

const PLANTA_HTTP = {
  id: 1,
  slug: "monstera",
  nombre_comun: "Monstera",
  nombre_cientifico: "Monstera deliciosa",
  luz: "indirecta",
  riego: "moderado",
};

describe("PlantaHttpAdapter.listarPlantas", () => {
  it("consulta GET plantas y traduce los campos a camelCase", async () => {
    const cliente = crearCliente();
    cliente.get.mockResolvedValue(respuesta(200, { plantas: [PLANTA_HTTP] }));

    const resultado = await new PlantaHttpAdapter(cliente).listarPlantas();

    expect(cliente.get).toHaveBeenCalledWith("plantas");
    expect(resultado).toEqual({
      estado: "exito",
      valor: [
        {
          id: 1,
          slug: "monstera",
          nombreComun: "Monstera",
          nombreCientifico: "Monstera deliciosa",
          luz: "indirecta",
          riego: "moderado",
        },
      ],
    });
  });

  it("acepta un catálogo vacío", async () => {
    const cliente = crearCliente();
    cliente.get.mockResolvedValue(respuesta(200, { plantas: [] }));

    const resultado = await new PlantaHttpAdapter(cliente).listarPlantas();

    expect(resultado).toEqual({ estado: "exito", valor: [] });
  });

  it.each([
    [401, "sesion_vencida"],
    [404, "desconocido"],
    [500, "desconocido"],
  ])("traduce el estado HTTP %i", async (estado, tipo) => {
    const cliente = crearCliente();
    cliente.get.mockResolvedValue(respuesta(estado));

    const resultado = await new PlantaHttpAdapter(cliente).listarPlantas();

    expect(resultado.estado).toBe("error");
    if (resultado.estado === "error") {
      expect(resultado.error.tipo).toBe(tipo);
    }
  });

  it.each([
    ["sin cuerpo", undefined],
    ["cuerpo sin plantas", { otra: [] }],
    ["plantas no es lista", { plantas: "x" }],
    ["planta sin slug", { plantas: [{ ...PLANTA_HTTP, slug: undefined }] }],
    ["id no numérico", { plantas: [{ ...PLANTA_HTTP, id: "1" }] }],
    ["elemento no objeto", { plantas: [3] }],
  ])("rechaza una respuesta mal formada (%s)", async (_nombre, cuerpo) => {
    const cliente = crearCliente();
    cliente.get.mockResolvedValue(respuesta(200, cuerpo));

    const resultado = await new PlantaHttpAdapter(cliente).listarPlantas();

    expect(resultado).toEqual({ estado: "error", error: { tipo: "desconocido" } });
  });

  it.each([
    ["conexion", "conexion"],
    ["desconocido", "desconocido"],
  ] as const)("traduce el fallo de red %s", async (motivo, tipo) => {
    const cliente = crearCliente();
    cliente.get.mockResolvedValue({ tipo: "fallo", motivo });

    const resultado = await new PlantaHttpAdapter(cliente).listarPlantas();

    expect(resultado).toEqual({ estado: "error", error: { tipo } });
  });
});

describe("PlantaHttpAdapter.vincular", () => {
  it("envía POST materas/{id}/planta con planta_id", async () => {
    const cliente = crearCliente();
    cliente.post.mockResolvedValue(respuesta(200, { mensaje: "Planta vinculada" }));

    const resultado = await new PlantaHttpAdapter(cliente).vincular(12, 2);

    expect(resultado).toEqual({ estado: "exito", valor: undefined });
    expect(cliente.post).toHaveBeenCalledWith("materas/12/planta", {
      planta_id: 2,
    });
  });

  it.each([
    [400, "validacion"],
    [401, "sesion_vencida"],
    [404, "no_encontrado"],
    [409, "desconocido"],
    [500, "desconocido"],
  ])("traduce el estado HTTP %i", async (estado, tipo) => {
    const cliente = crearCliente();
    cliente.post.mockResolvedValue(respuesta(estado));

    const resultado = await new PlantaHttpAdapter(cliente).vincular(12, 2);

    expect(resultado.estado).toBe("error");
    if (resultado.estado === "error") {
      expect(resultado.error.tipo).toBe(tipo);
    }
  });

  it("traduce timeout y red caída a conexión", async () => {
    const cliente = crearCliente();
    cliente.post.mockResolvedValue({ tipo: "fallo", motivo: "conexion" });

    const resultado = await new PlantaHttpAdapter(cliente).vincular(12, 2);

    expect(resultado).toEqual({ estado: "error", error: { tipo: "conexion" } });
  });
});
