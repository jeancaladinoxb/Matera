import { ErrorValidacionDominio } from "./errores-dominio";

export class ContraseñaDeInicioSesionInvalidaError extends ErrorValidacionDominio {
  constructor() {
    super("La contraseña es obligatoria.");
  }
}

export class ContraseñaDeInicioSesion {
  readonly valor: string;

  constructor(valor: string) {
    if (typeof valor !== "string" || valor.length === 0) {
      throw new ContraseñaDeInicioSesionInvalidaError();
    }

    this.valor = valor;
  }
}
