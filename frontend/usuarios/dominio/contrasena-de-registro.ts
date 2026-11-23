import { ContraseñaDeRegistroInvalidaError } from "./errores-dominio";

const ES_ALFANUMERICA = /^[\p{L}\p{N}]+$/u;
const CONTIENE_MAYUSCULA = /\p{Uppercase}/u;

export class ContraseñaDeRegistro {
  readonly valor: string;

  constructor(valor: string) {
    if (
      typeof valor !== "string" ||
      Array.from(valor).length < 8 ||
      !ES_ALFANUMERICA.test(valor) ||
      !CONTIENE_MAYUSCULA.test(valor)
    ) {
      throw new ContraseñaDeRegistroInvalidaError();
    }

    this.valor = valor;
  }
}
