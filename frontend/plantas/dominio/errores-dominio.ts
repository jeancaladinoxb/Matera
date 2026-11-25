export class ErrorValidacionPlanta extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = new.target.name;
  }
}

export class PlantaInvalidaError extends ErrorValidacionPlanta {
  constructor() {
    super("La planta no es válida.");
  }
}

export class IdentificadorMateraInvalidoError extends ErrorValidacionPlanta {
  constructor() {
    super("La matera no es válida.");
  }
}

export class IdentificadorPlantaInvalidoError extends ErrorValidacionPlanta {
  constructor() {
    super("Elige una planta válida.");
  }
}
