export class ErrorValidacionGamificacion extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = new.target.name;
  }
}

export class LogroInvalidoError extends ErrorValidacionGamificacion {
  constructor() {
    super("Los datos del logro no son válidos.");
  }
}

export class PerfilGamificacionInvalidoError extends ErrorValidacionGamificacion {
  constructor() {
    super("Los datos de gamificación no son válidos.");
  }
}
