export class ErrorValidacionDominio extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = new.target.name;
  }
}

export class CorreoElectronicoInvalidoError extends ErrorValidacionDominio {
  constructor() {
    super("El correo electrónico no tiene un formato válido.");
  }
}

export class ContraseñaDeRegistroInvalidaError extends ErrorValidacionDominio {
  constructor() {
    super(
      "La contraseña debe tener al menos 8 caracteres, ser alfanumérica y contener al menos una mayúscula.",
    );
  }
}
