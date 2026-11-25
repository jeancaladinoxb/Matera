import { PanelPrincipalInvalidoError } from "./errores-dominio";
import { Matera } from "./matera";
import { Usuario } from "./usuario";

export class PanelPrincipal {
  readonly usuario: Usuario;
  readonly materas: readonly Matera[];
  readonly tieneOpcionGamificacion = true;
  readonly gamificacionDisponible = true;

  constructor(usuario: Usuario, materas: readonly Matera[]) {
    if (
      !(usuario instanceof Usuario) ||
      !Array.isArray(materas) ||
      materas.some((matera) => !(matera instanceof Matera))
    ) {
      throw new PanelPrincipalInvalidoError();
    }

    this.usuario = usuario;
    this.materas = Object.freeze([...materas]);
  }
}
