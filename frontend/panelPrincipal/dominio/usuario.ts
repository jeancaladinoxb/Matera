import { UsuarioPanelInvalidoError } from "./errores-dominio";

export interface DatosUsuario {
  readonly usuarioId: number;
  readonly nombre: string;
  readonly nickname: string;
}

export class Usuario {
  readonly usuarioId: number;
  readonly nombre: string;
  readonly nickname: string;

  constructor(datos: DatosUsuario) {
    if (
      !Number.isSafeInteger(datos.usuarioId) ||
      datos.usuarioId <= 0 ||
      typeof datos.nombre !== "string" ||
      datos.nombre.trim().length === 0 ||
      typeof datos.nickname !== "string" ||
      datos.nickname.trim().length === 0
    ) {
      throw new UsuarioPanelInvalidoError();
    }

    this.usuarioId = datos.usuarioId;
    this.nombre = datos.nombre;
    this.nickname = datos.nickname;
  }
}
