import { describe, expect, it } from "vitest";

import { LogroInvalidoError } from "../errores-dominio";
import { DatosLogro, Logro } from "../logro";

const base: DatosLogro = {
  codigo: "jardin_en_casa",
  nombre: "Jardín en casa",
  descripcion: "Ten 3 materas vinculadas.",
  icono: "🪴",
  puntos: 25,
  progreso: 2,
  meta: 3,
  desbloqueado: false,
  fechaDesbloqueo: null,
};

describe("Logro", () => {
  it("calcula el porcentaje de progreso", () => {
    expect(new Logro(base).porcentaje).toBe(67);
  });

  it("acepta un logro desbloqueado con fecha", () => {
    const logro = new Logro({
      ...base,
      progreso: 3,
      desbloqueado: true,
      fechaDesbloqueo: new Date("2026-11-01T15:30:00Z"),
    });
    expect(logro.desbloqueado).toBe(true);
    expect(logro.porcentaje).toBe(100);
  });

  it.each<Partial<DatosLogro>>([
    { codigo: " " },
    { meta: 0 },
    { progreso: 4 },
    { puntos: -1 },
    { desbloqueado: true },
    { fechaDesbloqueo: new Date("2026-11-01") },
    { desbloqueado: true, fechaDesbloqueo: new Date("no es fecha") },
  ])("rechaza datos incoherentes %o", (cambio) => {
    expect(() => new Logro({ ...base, ...cambio })).toThrow(LogroInvalidoError);
  });
});
