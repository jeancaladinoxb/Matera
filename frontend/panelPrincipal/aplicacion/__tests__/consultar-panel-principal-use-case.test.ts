import { describe, expect, it } from "vitest";

import {
  fallo,
  exito,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { ConsultarPanelPrincipalUseCase } from "../casos-de-uso/consultar-panel-principal-use-case";
import {
  DatosPanelPrincipal,
  PanelRepositoryPort,
} from "../puertos/salida/panel-repository-port";

class FakePanelRepository implements PanelRepositoryPort {
  resultado: ResultadoAplicacion<DatosPanelPrincipal> = exito({
    usuario: { usuarioId: 7, nombre: "Ana", nickname: "anap" },
    materas: [],
  });
  llamadas = 0;

  async consultarPanel(): Promise<ResultadoAplicacion<DatosPanelPrincipal>> {
    this.llamadas += 1;
    return this.resultado;
  }
}

describe("ConsultarPanelPrincipalUseCase", () => {
  it("construye el panel con varias materas desde una sola consulta", async () => {
    const repository = new FakePanelRepository();
    repository.resultado = exito({
      usuario: { usuarioId: 7, nombre: "Ana", nickname: "anap" },
      materas: [
        {
          materaId: 12,
          dispositivoId: 12,
          plantaId: null,
          mac: "E072A1D55B18",
        },
        {
          materaId: 13,
          dispositivoId: 13,
          plantaId: 5,
          mac: "246F28AB1234",
        },
      ],
    });
    const useCase = new ConsultarPanelPrincipalUseCase(repository);

    const resultado = await useCase.consultarPanelPrincipal();

    expect(resultado.estado).toBe("exito");
    if (resultado.estado === "exito") {
      expect(resultado.valor.usuario.usuarioId).toBe(7);
      expect(resultado.valor.materas).toHaveLength(2);
      expect(resultado.valor.materas[0].sugerirVincularPlanta).toBe(true);
    }
    expect(repository.llamadas).toBe(1);
  });

  it("considera válido un panel sin materas", async () => {
    const useCase = new ConsultarPanelPrincipalUseCase(
      new FakePanelRepository(),
    );

    const resultado = await useCase.consultarPanelPrincipal();

    expect(resultado.estado).toBe("exito");
    if (resultado.estado === "exito") {
      expect(resultado.valor.materas).toEqual([]);
    }
  });

  it.each([
    { tipo: "sesion_vencida" as const },
    { tipo: "conexion" as const },
    { tipo: "desconocido" as const },
  ])("propaga errores de aplicación: $tipo", async (error) => {
    const repository = new FakePanelRepository();
    repository.resultado = fallo(error);
    const useCase = new ConsultarPanelPrincipalUseCase(repository);

    const resultado = await useCase.consultarPanelPrincipal();

    expect(resultado).toEqual(fallo(error));
  });

  it("traduce datos inválidos a error desconocido", async () => {
    const repository = new FakePanelRepository();
    repository.resultado = exito({
      usuario: { usuarioId: 0, nombre: "Ana", nickname: "anap" },
      materas: [],
    });
    const useCase = new ConsultarPanelPrincipalUseCase(repository);

    const resultado = await useCase.consultarPanelPrincipal();

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });
});
