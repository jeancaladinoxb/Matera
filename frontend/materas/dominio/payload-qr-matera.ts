import { DireccionMac } from "./direccion-mac";
import { CodigoDeVinculacion } from "./codigo-de-vinculacion";
import { PayloadQrMateraInvalidoError } from "./errores-dominio";

export class PayloadQrMatera {
  readonly mac: DireccionMac;
  readonly codigo: CodigoDeVinculacion;

  constructor(texto: string) {
    if (typeof texto !== "string") {
      throw new PayloadQrMateraInvalidoError();
    }

    const coincidencia = /^MAT:(.+):([0-9A-Fa-f]{12})$/.exec(texto.trim());
    if (!coincidencia) {
      throw new PayloadQrMateraInvalidoError();
    }

    try {
      this.mac = new DireccionMac(coincidencia[1]);
      this.codigo = new CodigoDeVinculacion(coincidencia[2]);
    } catch {
      throw new PayloadQrMateraInvalidoError();
    }
  }
}
