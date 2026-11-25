import { describe, expect, it } from "vitest";

import {
  exito,
  fallo,
  ResultadoAplicacion,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { PerfilGamificacion } from "../../dominio/perfil-gamificacion";
import { ConsultarLogrosUseCase } from "../casos-de-uso/consultar-logros-use-case";
import {
  DatosPerfilGamificacion,
  LogrosRepositoryPort,
} from "../puertos/salida/logros-repository-port";

const datosValidos: DatosPerfilGamificacion = {
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
      fechaDesbloqueo: new Date("2026-11-01T00:00:00Z"),
    },
  ],
};

class FakeLogrosRepository implements LogrosRepositoryPort {
  resultado: ResultadoAplicacion<DatosPerfilGamificacion> = exito(datosValidos);

  async consultarLogros() {
    return this.resultado;
  }
}

describe("ConsultarLogrosUseCase", () => {
  it("construye el perfil de dominio", async () => {
    const resultado = await new ConsultarLogrosUseCase(
      new FakeLogrosRepository(),
    ).consultarLogros();

    expect(resultado.estado).toBe("exito");
    if (resultado.estado === "exito") {
      expect(resultado.valor).toBeInstanceOf(PerfilGamificacion);
      expect(resultado.valor.logrosDesbloqueados).toBe(1);
    }
  });

  it("propaga errores del repositorio", async () => {
    const repository = new FakeLogrosRepository();
    repository.resultado = fallo({ tipo: "sesion_vencida" });

    const resultado = await new ConsultarLogrosUseCase(repository).consultarLogros();

    expect(resultado).toEqual(fallo({ tipo: "sesion_vencida" }));
  });

  it("convierte datos inválidos en error desconocido", async () => {
    const repository = new FakeLogrosRepository();
    repository.resultado = exito({ ...datosValidos, puntos: -5 });

    const resultado = await new ConsultarLogrosUseCase(repository).consultarLogros();

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });
});
