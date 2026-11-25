import { Planta } from "../../dominio/planta";

export function normalizarTexto(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .trim();
}

export function filtrarPlantas(
  plantas: readonly Planta[],
  busqueda: string,
): readonly Planta[] {
  const consulta = normalizarTexto(busqueda);
  if (consulta === "") {
    return plantas;
  }
  return plantas.filter((planta) =>
    normalizarTexto(`${planta.nombreComun} ${planta.nombreCientifico}`).includes(
      consulta,
    ),
  );
}

export function etiquetaMatera(mac: string): string {
  return `Matera ···${mac.trim().slice(-4).toUpperCase()}`;
}

export function textoLuz(planta: Planta): string {
  return `Luz ${planta.luz}`;
}

export function textoRiego(planta: Planta): string {
  return `Riego ${planta.riego}`;
}
