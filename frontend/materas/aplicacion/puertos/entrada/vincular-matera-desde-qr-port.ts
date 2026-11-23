import {
  ResultadoAplicacion,
} from "../../../../usuarios/aplicacion/resultado-aplicacion";

export interface VincularMateraDesdeQrPort {
  vincularDesdeQr(
    textoQr: string,
  ): Promise<ResultadoAplicacion<void>>;
}
