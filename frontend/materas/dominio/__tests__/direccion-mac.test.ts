import { describe, expect, it } from "vitest";

import { DireccionMac } from "../direccion-mac";
import {
  DireccionMacInvalidaError,
  ErrorValidacionMatera,
} from "../errores-dominio";

describe("DireccionMac", () => {
  it.each([
    ["24:6f:28:ab:12:34", "246F28AB1234"],
    ["24-6F-28-AB-12-34", "246F28AB1234"],
    ["24.6f.28.ab.12.34", "246F28AB1234"],
    ["246f28ab1234", "246F28AB1234"],
  ])("normaliza %s a %s", (entrada, esperada) => {
    expect(new DireccionMac(entrada).valor).toBe(esperada);
  });

  it.each(["", "246F28AB123", "246F28AB12G4", "24:6F:28:AB:12", "  "])(
    "rechaza %s con un error propio",
    (entrada) => {
      expect(() => new DireccionMac(entrada)).toThrow(DireccionMacInvalidaError);
      expect(() => new DireccionMac(entrada)).toThrow(ErrorValidacionMatera);
    },
  );
});
