import { describe, expect, it } from "vitest";

import { CodigoDeVinculacion } from "../codigo-de-vinculacion";
import {
  CodigoDeVinculacionInvalidoError,
  ErrorValidacionMatera,
} from "../errores-dominio";

describe("CodigoDeVinculacion", () => {
  it("normaliza el código válido a minúsculas", () => {
    const codigo = new CodigoDeVinculacion("9F3A1C7E0B52");

    expect(codigo.obtenerValor()).toBe("9f3a1c7e0b52");
  });

  it.each(["", "9f3a1c7e0b5", "9f3a1c7e0b5!", "gggggggggggg", "  "])(
    "rechaza %s con un error propio",
    (entrada) => {
      expect(() => new CodigoDeVinculacion(entrada)).toThrow(
        CodigoDeVinculacionInvalidoError,
      );
      expect(() => new CodigoDeVinculacion(entrada)).toThrow(
        ErrorValidacionMatera,
      );
    },
  );

  it("no expone representación textual ni serialización JSON automática", () => {
    const codigo = new CodigoDeVinculacion("9F3A1C7E0B52");

    expect(String(codigo)).not.toContain("9f3a1c7e0b52");
    expect(JSON.stringify(codigo)).not.toContain("9f3a1c7e0b52");
    expect(JSON.stringify(codigo)).toBe("{}");
  });
});
