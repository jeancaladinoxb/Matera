import { describe, expect, it } from "vitest";

import { ErrorValidacionPanelPrincipal, MateraPanelInvalidaError } from "../errores-dominio";
import { Matera } from "../matera";

describe("Matera del panel", () => {
  it("sugiere vincular una planta cuando no tiene planta asignada", () => {
    const matera = new Matera({
      materaId: 12,
      dispositivoId: 12,
      plantaId: null,
      mac: "E072A1D55B18",
    });

    expect(matera.sugerirVincularPlanta).toBe(true);
  });

  it("no sugiere vincular una planta si ya tiene una asignada", () => {
    const matera = new Matera({
      materaId: 12,
      dispositivoId: 12,
      plantaId: 5,
      mac: "E072A1D55B18",
    });

    expect(matera.sugerirVincularPlanta).toBe(false);
  });

  it("rechaza identificadores y MAC vacíos", () => {
    const datos = {
      materaId: 0,
      dispositivoId: 12,
      plantaId: null,
      mac: "E072A1D55B18",
    };

    expect(() => new Matera(datos)).toThrow(MateraPanelInvalidaError);
    expect(() => new Matera(datos)).toThrow(ErrorValidacionPanelPrincipal);
    expect(() => new Matera({ ...datos, materaId: 12, mac: " " })).toThrow(
      MateraPanelInvalidaError,
    );
  });
});
