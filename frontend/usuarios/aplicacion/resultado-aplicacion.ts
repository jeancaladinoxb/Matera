import { ErrorAplicacion } from "./errores-aplicacion";

export type ResultadoAplicacion<T> =
  | { readonly estado: "exito"; readonly valor: T }
  | { readonly estado: "error"; readonly error: ErrorAplicacion };

export function exito<T>(valor: T): ResultadoAplicacion<T> {
  return { estado: "exito", valor };
}

export function fallo<T>(error: ErrorAplicacion): ResultadoAplicacion<T> {
  return { estado: "error", error };
}
