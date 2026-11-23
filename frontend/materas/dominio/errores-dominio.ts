export class ErrorValidacionMatera extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = new.target.name;
  }
}

export class DireccionMacInvalidaError extends ErrorValidacionMatera {
  constructor() {
    super("La MAC no tiene un formato válido.");
  }
}

export class CodigoDeVinculacionInvalidoError extends ErrorValidacionMatera {
  constructor() {
    super("El código de vinculación no tiene un formato válido.");
  }
}

export class PayloadQrMateraInvalidoError extends ErrorValidacionMatera {
  constructor() {
    super("El código QR no corresponde a una matera.");
  }
}
