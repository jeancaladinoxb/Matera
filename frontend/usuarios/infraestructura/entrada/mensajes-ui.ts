import { ErrorAplicacion } from "../../aplicacion/errores-aplicacion";

export function mensajeDeError(error: ErrorAplicacion): string {
  switch (error.tipo) {
    case "validacion":
      return error.mensaje;
    case "correo_duplicado":
      return "No se pudo completar el registro. Revisa los datos e inténtalo de nuevo.";
    case "credenciales_invalidas":
      return "El correo o la contraseña no son correctos.";
    case "conexion":
      return "No hay conexión. Revisa tu internet e inténtalo de nuevo.";
    case "desconocido":
      return "Ocurrió un error inesperado. Inténtalo de nuevo.";
  }
}
