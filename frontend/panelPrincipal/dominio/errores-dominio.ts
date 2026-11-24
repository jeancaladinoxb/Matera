export class ErrorValidacionPanelPrincipal extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = new.target.name;
  }
}

export class UsuarioPanelInvalidoError extends ErrorValidacionPanelPrincipal {
  constructor() {
    super("Los datos del usuario no son válidos.");
  }
}

export class MateraPanelInvalidaError extends ErrorValidacionPanelPrincipal {
  constructor() {
    super("Los datos de la matera no son válidos.");
  }
}

export class PanelPrincipalInvalidoError extends ErrorValidacionPanelPrincipal {
  constructor() {
    super("Los datos del panel principal no son válidos.");
  }
}
