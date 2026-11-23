import { describe, expect, it } from "vitest";

import { CorreoElectronico } from "../correo-electronico";
import {
  CorreoElectronicoInvalidoError,
  ErrorValidacionDominio,
} from "../errores-dominio";

describe("CorreoElectronico", () => {
  it("recorta y normaliza el correo a minúsculas", () => {
    expect(new CorreoElectronico(" Ana@Example.COM ").valor).toBe(
      "ana@example.com",
    );
  });

  it("acepta formatos válidos compatibles con el backend", () => {
    expect(new CorreoElectronico("ana.perez+mate@example.co")).toBeInstanceOf(
      CorreoElectronico,
    );
  });

  it.each([
    "",
    "correo-invalido",
    "ana@localhost",
    "ana..perez@example.com",
    "ana@-example.com",
    `${"a".repeat(243)}@example.com`,
  ])("rechaza el correo inválido %s con un error propio", (valor) => {
    expect(() => new CorreoElectronico(valor)).toThrow(
      CorreoElectronicoInvalidoError,
    );
    expect(() => new CorreoElectronico(valor)).toThrow(ErrorValidacionDominio);
  });
});
