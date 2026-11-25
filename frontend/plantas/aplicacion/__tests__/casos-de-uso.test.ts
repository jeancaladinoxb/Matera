import { describe, expect, it, vi } from "vitest";

import { exito, fallo } from "../../../usuarios/aplicacion/resultado-aplicacion";
import { DatosPlanta, Planta } from "../../dominio/planta";
import { ListarPlantasUseCase } from "../casos-de-uso/listar-plantas-use-case";
import { VincularPlantaUseCase } from "../casos-de-uso/vincular-planta-use-case";
import { PlantaRepositoryPort } from "../puertos/salida/planta-repository-port";

const MONSTERA: DatosPlanta = {
  id: 1,
  slug: "monstera",
  nombreComun: "Monstera",
  nombreCientifico: "Monstera deliciosa",
  luz: "indirecta",
  riego: "moderado",
};

function crearRepository() {
  return {
    listarPlantas: vi.fn<PlantaRepositoryPort["listarPlantas"]>(),
    vincular: vi.fn<PlantaRepositoryPort["vincular"]>(),
  } satisfies PlantaRepositoryPort;
}

describe("ListarPlantasUseCase", () => {
  it("convierte los datos del repositorio en entidades Planta", async () => {
    const repository = crearRepository();
    repository.listarPlantas.mockResolvedValue(exito([MONSTERA]));
    const useCase = new ListarPlantasUseCase(repository);

    const resultado = await useCase.listarPlantas();

    expect(resultado.estado).toBe("exito");
    if (resultado.estado === "exito") {
      expect(resultado.valor).toHaveLength(1);
      expect(resultado.valor[0]).toBeInstanceOf(Planta);
      expect(resultado.valor[0].nombreComun).toBe("Monstera");
    }
  });

  it("propaga los errores tipados del puerto", async () => {
    const repository = crearRepository();
    repository.listarPlantas.mockResolvedValue(
      fallo({ tipo: "sesion_vencida" }),
    );

    const resultado = await new ListarPlantasUseCase(repository).listarPlantas();

    expect(resultado).toEqual(fallo({ tipo: "sesion_vencida" }));
  });

  it("devuelve error desconocido si una planta del servidor no es válida", async () => {
    const repository = crearRepository();
    repository.listarPlantas.mockResolvedValue(
      exito([{ ...MONSTERA, luz: "sol" }]),
    );

    const resultado = await new ListarPlantasUseCase(repository).listarPlantas();

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });

  it("traduce una excepción inesperada del puerto a error desconocido", async () => {
    const repository = crearRepository();
    repository.listarPlantas.mockRejectedValue(new Error("boom"));

    const resultado = await new ListarPlantasUseCase(repository).listarPlantas();

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });
});

describe("VincularPlantaUseCase", () => {
  it("delega la vinculación con los ids", async () => {
    const repository = crearRepository();
    repository.vincular.mockResolvedValue(exito(undefined));
    const useCase = new VincularPlantaUseCase(repository);

    const resultado = await useCase.vincularPlanta({ materaId: 12, plantaId: 2 });

    expect(resultado).toEqual(exito(undefined));
    expect(repository.vincular).toHaveBeenCalledWith(12, 2);
  });

  it.each([
    { materaId: 0, plantaId: 2 },
    { materaId: -1, plantaId: 2 },
    { materaId: 1.5, plantaId: 2 },
    { materaId: 12, plantaId: 0 },
    { materaId: 12, plantaId: Number.NaN },
  ])("rechaza ids inválidos antes de tocar el puerto: %j", async (solicitud) => {
    const repository = crearRepository();

    const resultado = await new VincularPlantaUseCase(repository).vincularPlanta(
      solicitud,
    );

    expect(resultado.estado).toBe("error");
    if (resultado.estado === "error") {
      expect(resultado.error.tipo).toBe("validacion");
    }
    expect(repository.vincular).not.toHaveBeenCalled();
  });

  it.each(["sesion_vencida", "no_encontrado", "conexion"] as const)(
    "propaga el error tipado %s",
    async (tipo) => {
      const repository = crearRepository();
      repository.vincular.mockResolvedValue(fallo<void>({ tipo }));

      const resultado = await new VincularPlantaUseCase(repository).vincularPlanta({
        materaId: 12,
        plantaId: 2,
      });

      expect(resultado).toEqual(fallo({ tipo }));
    },
  );

  it("traduce una excepción inesperada a error desconocido", async () => {
    const repository = crearRepository();
    repository.vincular.mockRejectedValue(new Error("boom"));

    const resultado = await new VincularPlantaUseCase(repository).vincularPlanta({
      materaId: 12,
      plantaId: 2,
    });

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });
});
