import { describe, expect, it } from "vitest";

import { PayloadQrMatera } from "../payload-qr-matera";
import {
  PayloadQrMateraInvalidoError,
  ErrorValidacionMatera,
} from "../errores-dominio";

describe("PayloadQrMatera", () => {
  it("interpreta el texto QR y entrega MAC y código normalizados", () => {
    const payload = new PayloadQrMatera("MAT:246F28AB1234:9F3A1C7E0B52");

    expect(payload.mac.valor).toBe("246F28AB1234");
    expect(payload.codigo.obtenerValor()).toBe("9f3a1c7e0b52");
  });

  it("también interpreta una MAC separada dentro del payload", () => {
    const payload = new PayloadQrMatera("MAT:24:6f:28:ab:12:34:9F3A1C7E0B52");

    expect(payload.mac.valor).toBe("246F28AB1234");
    expect(payload.codigo.obtenerValor()).toBe("9f3a1c7e0b52");
  });

  it.each([
    "",
    "MAT-246F28AB1234-9f3a1c7e0b52",
    "MAT:246F28AB1234",
    "MAT:246F28AB12G4:9f3a1c7e0b52",
    "MAT:246F28AB1234:9f3a1c7e0b5!",
  ])("rechaza el payload %s", (entrada) => {
    expect(() => new PayloadQrMatera(entrada)).toThrow(
      PayloadQrMateraInvalidoError,
    );
    expect(() => new PayloadQrMatera(entrada)).toThrow(ErrorValidacionMatera);
  });
});
