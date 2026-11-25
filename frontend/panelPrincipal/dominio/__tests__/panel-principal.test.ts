import { describe, expect, it } from "vitest";

import { Matera } from "../matera";
import { PanelPrincipal } from "../panel-principal";
import { Usuario } from "../usuario";

describe("PanelPrincipal", () => {
  const usuario = new Usuario({
    usuarioId: 7,
    nombre: "Ana",
    nickname: "anap",
  });

  it("acepta un usuario sin materas", () => {
    const panel = new PanelPrincipal(usuario, []);

    expect(panel.materas).toEqual([]);
  });

  it("conserva varias materas y ofrece gamificación no disponible", () => {
    const panel = new PanelPrincipal(usuario, [
      new Matera({
        materaId: 12,
        dispositivoId: 12,
        plantaId: null,
        mac: "E072A1D55B18",
      }),
      new Matera({
        materaId: 13,
        dispositivoId: 13,
        plantaId: 5,
        mac: "246F28AB1234",
      }),
    ]);

    expect(panel.materas).toHaveLength(2);
    expect(panel.tieneOpcionGamificacion).toBe(true);
    expect(panel.gamificacionDisponible).toBe(true);
  });
});
