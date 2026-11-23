import {
  ResultadoAplicacion,
} from "../../../../usuarios/aplicacion/resultado-aplicacion";

export interface MateraDelUsuario {
  readonly vinculada: boolean;
  readonly mac?: string;
}

export interface ConsultarMateraDelUsuarioPort {
  consultarMateraDelUsuario(): Promise<
    ResultadoAplicacion<MateraDelUsuario>
  >;
}
