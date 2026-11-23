import { DireccionMacInvalidaError } from "./errores-dominio";

const MAC_NORMALIZADA = /^[0-9A-F]{12}$/;

export class DireccionMac {
  readonly valor: string;

  constructor(valor: string) {
    if (typeof valor !== "string") {
      throw new DireccionMacInvalidaError();
    }

    const normalizada = valor.trim().replace(/[:.\-]/g, "").toUpperCase();
    if (!MAC_NORMALIZADA.test(normalizada)) {
      throw new DireccionMacInvalidaError();
    }

    this.valor = normalizada;
  }
}
