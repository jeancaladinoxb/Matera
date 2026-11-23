import { CorreoElectronicoInvalidoError } from "./errores-dominio";

const FORMATO_CORREO =
  /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;

export class CorreoElectronico {
  readonly valor: string;

  constructor(valor: string) {
    if (typeof valor !== "string") {
      throw new CorreoElectronicoInvalidoError();
    }

    const normalizado = valor.trim().toLowerCase();
    if (
      normalizado.length > 254 ||
      !FORMATO_CORREO.test(normalizado)
    ) {
      throw new CorreoElectronicoInvalidoError();
    }

    this.valor = normalizado;
  }
}
