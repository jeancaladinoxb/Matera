import { CodigoDeVinculacionInvalidoError } from "./errores-dominio";

const CODIGO_HEXADECIMAL = /^[0-9A-Fa-f]{12}$/;
const SECRETOS = new WeakMap<CodigoDeVinculacion, string>();

export class CodigoDeVinculacion {
  constructor(valor: string) {
    if (typeof valor !== "string" || !CODIGO_HEXADECIMAL.test(valor)) {
      throw new CodigoDeVinculacionInvalidoError();
    }

    SECRETOS.set(this, valor.trim().toLowerCase());
  }

  obtenerValor(): string {
    const secreto = SECRETOS.get(this);
    if (secreto === undefined) {
      throw new CodigoDeVinculacionInvalidoError();
    }
    return secreto;
  }
}
