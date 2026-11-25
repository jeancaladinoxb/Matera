import { describe, expect, it } from "vitest";

import { Planta } from "../../../dominio/planta";
import {
  etiquetaMatera,
  filtrarPlantas,
  normalizarTexto,
  textoLuz,
  textoRiego,
} from "../presentacion-plantas";

function crearPlanta(
  id: number,
  slug: string,
  nombreComun: string,
  nombreCientifico: string,
): Planta {
  return new Planta({
    id,
    slug,
    nombreComun,
    nombreCientifico,
    luz: "indirecta",
    riego: "moderado",
  });
}

const PLANTAS = [
  crearPlanta(1, "monstera", "Monstera", "Monstera deliciosa"),
  crearPlanta(2, "calathea", "Calathea", "Calathea orbifolia"),
  crearPlanta(3, "sansevieria", "Sansevieria", "Dracaena trifasciata"),
  crearPlanta(4, "pothos", "Pothos", "Epipremnum aureum"),
  crearPlanta(5, "bonsai", "Bonsái", "Ficus microcarpa"),
];

describe("normalizarTexto", () => {
  it("ignora tildes, mayúsculas y espacios en los bordes", () => {
    expect(normalizarTexto("  BONSÁI ")).toBe("bonsai");
    expect(normalizarTexto("Ñandú")).toBe("nandu");
  });
});

describe("filtrarPlantas", () => {
  it("devuelve todo si la búsqueda está vacía o en blanco", () => {
    expect(filtrarPlantas(PLANTAS, "")).toBe(PLANTAS);
    expect(filtrarPlantas(PLANTAS, "   ")).toBe(PLANTAS);
  });

  it("filtra por nombre común ignorando mayúsculas", () => {
    expect(filtrarPlantas(PLANTAS, "POTH").map((p) => p.id)).toEqual([4]);
  });

  it("ignora tildes en la búsqueda y en el catálogo", () => {
    expect(filtrarPlantas(PLANTAS, "bonsai").map((p) => p.id)).toEqual([5]);
    expect(filtrarPlantas(PLANTAS, "bonsái").map((p) => p.id)).toEqual([5]);
  });

  it("también busca en el nombre científico", () => {
    expect(filtrarPlantas(PLANTAS, "ficus").map((p) => p.id)).toEqual([5]);
    expect(filtrarPlantas(PLANTAS, "trifasciata").map((p) => p.id)).toEqual([3]);
  });

  it("devuelve una lista vacía si nada coincide", () => {
    expect(filtrarPlantas(PLANTAS, "baobab")).toEqual([]);
  });
});

describe("etiquetas", () => {
  it("muestra los últimos 4 caracteres de la MAC", () => {
    expect(etiquetaMatera("246F28AB1234")).toBe("Matera ···1234");
    expect(etiquetaMatera("e072a1d55b18")).toBe("Matera ···5B18");
  });

  it("describe luz y riego", () => {
    expect(textoLuz(PLANTAS[0])).toBe("Luz indirecta");
    expect(textoRiego(PLANTAS[0])).toBe("Riego moderado");
  });
});
