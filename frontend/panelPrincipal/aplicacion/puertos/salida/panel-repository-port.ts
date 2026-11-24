import { ResultadoAplicacion } from "../../../../usuarios/aplicacion/resultado-aplicacion";

export interface DatosUsuarioPanel {
  readonly usuarioId: number;
  readonly nombre: string;
  readonly nickname: string;
}

export interface DatosMateraPanel {
  readonly materaId: number;
  readonly dispositivoId: number;
  readonly plantaId: number | null;
  readonly mac: string;
}

export interface DatosPanelPrincipal {
  readonly usuario: DatosUsuarioPanel;
  readonly materas: readonly DatosMateraPanel[];
}

export interface PanelRepositoryPort {
  consultarPanel(): Promise<ResultadoAplicacion<DatosPanelPrincipal>>;
}
