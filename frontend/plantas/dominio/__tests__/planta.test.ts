import { describe, expect, it } from "vitest";

import {
  ErrorValidacionPlanta,
  PlantaInvalidaError,
} from "../errores-dominio";
import { DatosPlanta, Planta, esIdentificadorPositivo } from "../planta";

const DATOS: DatosPlanta = {
  id: 1,
  slug: "monstera",
  nombreComun: "Monstera",
  nombreCientifico: "Monstera deliciosa",
  luz: "indirecta",
  riego: "moderado",
};

describe("Planta", () => {
  it("crea una planta válida", () => {
    const planta = new Planta(DATOS);

    expect(planta).toMatchObject(DATOS);
  });

  it.each([0, -1, 1.5, Number.NaN, Number.MAX_SAFE_INTEGER + 2])(
    "rechaza el id %s",
    (id) => {
      expect(() => new Planta({ ...DATOS, id })).toThrow(PlantaInvalidaError);
    },
  );

  it.each(["", "Monstera", "mon-stera", "mon stera", "ñandú"])(
    "rechaza el slug %j",
    (slug) => {
      expect(() => new Planta({ ...DATOS, slug })).toThrow(PlantaInvalidaError);
    },
  );

  it.each(["nombreComun", "nombreCientifico"] as const)(
    "exige %s",
    (campo) => {
      expect(() => new Planta({ ...DATOS, [campo]: "   " })).toThrow(
        PlantaInvalidaError,
      );
    },
  );

  it.each(["baja", "indirecta", "directa"])("acepta la luz %s", (luz) => {
    expect(new Planta({ ...DATOS, luz }).luz).toBe(luz);
  });

  it.each(["bajo", "moderado", "alto"])("acepta el riego %s", (riego) => {
    expect(new Planta({ ...DATOS, riego }).riego).toBe(riego);
  });

  it("rechaza luz o riego desconocidos", () => {
    expect(() => new Planta({ ...DATOS, luz: "sol" })).toThrow(
      ErrorValidacionPlanta,
    );
    expect(() => new Planta({ ...DATOS, riego: "mucho" })).toThrow(
      ErrorValidacionPlanta,
    );
  });
});

describe("esIdentificadorPositivo", () => {
  it("solo acepta enteros seguros positivos", () => {
    expect(esIdentificadorPositivo(7)).toBe(true);
    for (const valor of [0, -2, 1.2, "3", null, undefined, true]) {
      expect(esIdentificadorPositivo(valor)).toBe(false);
    }
  });
});
