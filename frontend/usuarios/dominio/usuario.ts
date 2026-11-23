import { ErrorValidacionDominio } from "./errores-dominio";
import { CorreoElectronico } from "./correo-electronico";
import { ContraseñaDeRegistro } from "./contrasena-de-registro";

export class CamposDeUsuarioObligatoriosError extends ErrorValidacionDominio {
  constructor() {
    super("Nombre, apellido y nickname son obligatorios.");
  }
}

export interface DatosUsuario {
  readonly nombre: string;
  readonly apellido: string;
  readonly nickname: string;
  readonly correo: CorreoElectronico;
  readonly contrasena: ContraseñaDeRegistro;
}

export class Usuario {
  readonly nombre: string;
  readonly apellido: string;
  readonly nickname: string;
  readonly correo: CorreoElectronico;
  readonly contrasena: ContraseñaDeRegistro;

  constructor(datos: DatosUsuario) {
    if (
      [datos.nombre, datos.apellido, datos.nickname].some(
        (campo) => typeof campo !== "string" || campo.trim().length === 0,
      )
    ) {
      throw new CamposDeUsuarioObligatoriosError();
    }

    this.nombre = datos.nombre;
    this.apellido = datos.apellido;
    this.nickname = datos.nickname;
    this.correo = datos.correo;
    this.contrasena = datos.contrasena;
  }
}
