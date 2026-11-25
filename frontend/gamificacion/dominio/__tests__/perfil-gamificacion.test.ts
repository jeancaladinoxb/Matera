import { describe, expect, it } from "vitest";

import { PerfilGamificacionInvalidoError } from "../errores-dominio";
import { Logro } from "../logro";
import { PerfilGamificacion } from "../perfil-gamificacion";

const brote = { numero: 2, nombre: "Brote", puntosMinimos: 20 };
const plantula = { numero: 3, nombre: "Plántula", puntosMinimos: 50 };

const desbloqueado = new Logro({
  codigo: "primer_brote",
  nombre: "Primer brote",
  descripcion: "Vincula tu primera matera.",
  icono: "🌱",
  puntos: 10,
  progreso: 1,
  meta: 1,
  desbloqueado: true,
  fechaDesbloqueo: new Date("2026-11-01T00:00:00Z"),
});

describe("PerfilGamificacion", () => {
  it("calcula cuánto falta y el avance dentro del nivel", () => {
    const perfil = new PerfilGamificacion(35, brote, plantula, [desbloqueado]);

    expect(perfil.puntosParaSiguienteNivel).toBe(15);
    expect(perfil.porcentajeNivel).toBe(50);
    expect(perfil.logrosDesbloqueados).toBe(1);
  });

  it("en el nivel máximo muestra 100 %", () => {
    const perfil = new PerfilGamificacion(120, plantula, null, []);

    expect(perfil.puntosParaSiguienteNivel).toBe(0);
    expect(perfil.porcentajeNivel).toBe(100);
  });

  it("rechaza niveles incoherentes o logros inválidos", () => {
    expect(() => new PerfilGamificacion(-1, brote, plantula, [])).toThrow(
      PerfilGamificacionInvalidoError,
    );
    expect(() => new PerfilGamificacion(30, plantula, brote, [])).toThrow(
      PerfilGamificacionInvalidoError,
    );
    expect(
      () =>
        new PerfilGamificacion(30, brote, plantula, [
          {} as unknown as Logro,
        ]),
    ).toThrow(PerfilGamificacionInvalidoError);
  });
});
