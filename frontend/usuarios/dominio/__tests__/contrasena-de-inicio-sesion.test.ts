import { describe, expect, it } from "vitest";

import { ContraseñaDeInicioSesion } from "../contrasena-de-inicio-sesion";
import { ContraseñaDeInicioSesionInvalidaError } from "../contrasena-de-inicio-sesion";

describe("ContraseñaDeInicioSesion", () => {
  it("preserva la contraseña ingresada para autenticación", () => {
    expect(new ContraseñaDeInicioSesion("clave anterior!").valor).toBe(
      "clave anterior!",
    );
  });

  it("rechaza un valor vacío con un error propio", () => {
    expect(() => new ContraseñaDeInicioSesion("")).toThrow(
      ContraseñaDeInicioSesionInvalidaError,
    );
  });
});
