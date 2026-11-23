export type ErrorAplicacion =
  | { readonly tipo: "validacion"; readonly mensaje: string }
  | { readonly tipo: "correo_duplicado" }
  | { readonly tipo: "credenciales_invalidas" }
  | { readonly tipo: "conexion" }
  | { readonly tipo: "desconocido" };
