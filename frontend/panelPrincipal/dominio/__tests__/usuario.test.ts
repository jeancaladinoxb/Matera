import { describe, expect, it } from "vitest";

import { ErrorValidacionPanelPrincipal, UsuarioPanelInvalidoError } from "../errores-dominio";
import { Usuario } from "../usuario";

describe("Usuario del panel", () => {
  it("conserva su identificador, nombre y nickname", () => {
    const usuario = new Usuario({
      usuarioId: 7,
      nombre: "Ana",
      nickname: "anap",
    });

    expect(usuario).toMatchObject({
      usuarioId: 7,
      nombre: "Ana",
      nickname: "anap",
    });
  });

  it.each([
    { usuarioId: 0, nombre: "Ana", nickname: "anap" },
    { usuarioId: 7, nombre: "Ana", nickname: " " },
    { usuarioId: 7, nombre: "", nickname: "anap" },
  ])("rechaza datos incompletos", (datos) => {
    expect(() => new Usuario(datos)).toThrow(UsuarioPanelInvalidoError);
    expect(() => new Usuario(datos)).toThrow(ErrorValidacionPanelPrincipal);
  });
});
