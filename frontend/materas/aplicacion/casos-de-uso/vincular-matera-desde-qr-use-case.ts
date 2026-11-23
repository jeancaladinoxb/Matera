import { PayloadQrMatera } from "../../dominio/payload-qr-matera";
import { ErrorValidacionMatera } from "../../dominio/errores-dominio";
import {
  ResultadoAplicacion,
  fallo,
} from "../../../usuarios/aplicacion/resultado-aplicacion";
import { VincularMateraDesdeQrPort } from "../puertos/entrada/vincular-matera-desde-qr-port";
import { VincularMateraPort } from "../puertos/entrada/vincular-matera-port";

export class VincularMateraDesdeQrUseCase
  implements VincularMateraDesdeQrPort
{
  constructor(private readonly vincularMatera: VincularMateraPort) {}

  async vincularDesdeQr(
    textoQr: string,
  ): Promise<ResultadoAplicacion<void>> {
    let payload: PayloadQrMatera;

    try {
      payload = new PayloadQrMatera(textoQr);
    } catch (error) {
      if (error instanceof ErrorValidacionMatera) {
        return fallo<void>({
          tipo: "validacion",
          mensaje: error.message,
        });
      }
      throw error;
    }

    return this.vincularMatera.vincular({
      mac: payload.mac.valor,
      codigo: payload.codigo.obtenerValor(),
    });
  }
}
