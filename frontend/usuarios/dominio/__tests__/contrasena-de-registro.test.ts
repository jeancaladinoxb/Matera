import { describe, expect, it } from "vitest";

import { ContraseñaDeRegistro } from "../contrasena-de-registro";
import {
  ContraseñaDeRegistroInvalidaError,
  ErrorValidacionDominio,
} from "../errores-dominio";

describe("ContraseñaDeRegistro", () => {
  it("acepta contraseñas alfanuméricas con mayúscula y mínimo 8 caracteres", () => {
    expect(new ContraseñaDeRegistro("Clave123").valor).toBe("Clave123");
  });

  it("usa longitud de caracteres Unicode como el backend", () => {
    expect(() => new ContraseñaDeRegistro("𐐀abc123")).toThrow(
      ContraseñaDeRegistroInvalidaError,
    );
    expect(new ContraseñaDeRegistro("𐐀bcde123").valor).toBe("𐐀bcde123");
  });

  it.each(["", "clave123", "12345678", "Clave12", "Clave 123", "Clave123!"])(
    "rechaza la contraseña inválida %s con un error propio",
    (valor) => {
      expect(() => new ContraseñaDeRegistro(valor)).toThrow(
        ContraseñaDeRegistroInvalidaError,
      );
      expect(() => new ContraseñaDeRegistro(valor)).toThrow(
        ErrorValidacionDominio,
      );
    },
  );
});
