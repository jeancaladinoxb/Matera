export type ErrorAplicacion =
  | { readonly tipo: "validacion"; readonly mensaje: string }
  | { readonly tipo: "correo_duplicado" }
  | { readonly tipo: "credenciales_invalidas" }
  | { readonly tipo: "sesion_vencida" }
  | { readonly tipo: "matera_codigo_invalido" }
  | { readonly tipo: "matera_ya_vinculada" }
  | { readonly tipo: "conexion" }
  | { readonly tipo: "desconocido" };
