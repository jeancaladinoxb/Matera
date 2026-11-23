import { ContraseñaDeInicioSesion } from "../../dominio/contrasena-de-inicio-sesion";
import { CorreoElectronico } from "../../dominio/correo-electronico";
import { exito, fallo, ResultadoAplicacion } from "../../aplicacion/resultado-aplicacion";
import { SessionPort } from "../../aplicacion/puertos/salida/session-port";
import { ClienteHttp, ClienteHttpPort, ResultadoHttp } from "./cliente-http";

const INTERVALO_REFRESCO_MS = 15 * 60 * 1000;
const RETRASO_REINTENTO_INICIAL_MS = 1000;
const RETRASO_REINTENTO_MAXIMO_MS = 5 * 60 * 1000;

export type EventoSesion =
  | { readonly tipo: "refresco_rechazado" }
  | { readonly tipo: "refresco_fallido" };

type ObservadorSesion = (evento: EventoSesion) => void;

export class SessionHttpAdapter implements SessionPort {
  private temporizadorRefresco: ReturnType<typeof setTimeout> | undefined;
  private sesionActiva = false;
  private generacionSesion = 0;
  private retrasoReintentoMs = RETRASO_REINTENTO_INICIAL_MS;
  private refrescoEnCurso: Promise<void> | undefined;
  private readonly observadores = new Set<ObservadorSesion>();

  constructor(private readonly clienteHttp: ClienteHttpPort = new ClienteHttp()) {}

  async iniciarSesion(
    correo: CorreoElectronico,
    contrasena: ContraseñaDeInicioSesion,
  ): Promise<ResultadoAplicacion<void>> {
    const respuesta = await this.clienteHttp.post("login", {
      correo: correo.valor,
      contrasena: contrasena.valor,
    });

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo({ tipo: "conexion" })
        : fallo({ tipo: "desconocido" });
    }

    if (respuesta.estado === 200) {
      this.iniciarTemporizadorRefresco();
      return exito(undefined);
    }

    if (respuesta.estado === 401) {
      return fallo({ tipo: "credenciales_invalidas" });
    }

    if (respuesta.estado === 400) {
      return fallo({ tipo: "credenciales_invalidas" });
    }

    return fallo({ tipo: "desconocido" });
  }

  async cerrarSesion(): Promise<ResultadoAplicacion<void>> {
    this.limpiarTemporizadorRefresco();
    await this.refrescoEnCurso;
    const respuesta = await this.clienteHttp.post("logout");

    if (respuesta.tipo === "fallo") {
      return respuesta.motivo === "conexion"
        ? fallo({ tipo: "conexion" })
        : fallo({ tipo: "desconocido" });
    }

    return respuesta.estado === 204 || respuesta.estado === 200
      ? exito(undefined)
      : fallo({ tipo: "desconocido" });
  }

  observarEventos(observador: ObservadorSesion): () => void {
    this.observadores.add(observador);
    return () => {
      this.observadores.delete(observador);
    };
  }

  desmontar(): void {
    this.limpiarTemporizadorRefresco();
  }

  private iniciarTemporizadorRefresco(): void {
    this.limpiarTemporizadorRefresco();
    this.sesionActiva = true;
    this.retrasoReintentoMs = RETRASO_REINTENTO_INICIAL_MS;
    const generacion = this.generacionSesion;
    this.programarRefresco(INTERVALO_REFRESCO_MS, generacion);
  }

  private limpiarTemporizadorRefresco(): void {
    this.generacionSesion += 1;
    this.sesionActiva = false;
    if (this.temporizadorRefresco !== undefined) {
      clearTimeout(this.temporizadorRefresco);
      this.temporizadorRefresco = undefined;
    }
  }

  private programarRefresco(retrasoMs: number, generacion: number): void {
    if (!this.sesionActiva || generacion !== this.generacionSesion) {
      return;
    }
    this.temporizadorRefresco = setTimeout(
      () => this.iniciarRefresco(generacion),
      retrasoMs,
    );
  }

  private iniciarRefresco(generacion: number): void {
    const refresco = this.refrescarSesion(generacion);
    this.refrescoEnCurso = refresco;
    void refresco.then(() => {
      if (this.refrescoEnCurso === refresco) {
        this.refrescoEnCurso = undefined;
      }
    });
  }

  private async refrescarSesion(generacion: number): Promise<void> {
    if (!this.sesionActiva || generacion !== this.generacionSesion) {
      return;
    }

    const respuesta = await this.clienteHttp.post("session/refresh");
    if (!this.sesionActiva || generacion !== this.generacionSesion) {
      return;
    }

    if (respuesta.tipo === "fallo" && respuesta.motivo === "conexion") {
      this.programarRefresco(this.retrasoReintentoMs, generacion);
      this.retrasoReintentoMs = Math.min(
        this.retrasoReintentoMs * 2,
        RETRASO_REINTENTO_MAXIMO_MS,
      );
      return;
    }

    if (respuesta.tipo === "respuesta" && respuesta.estado === 200) {
      this.retrasoReintentoMs = RETRASO_REINTENTO_INICIAL_MS;
      this.programarRefresco(INTERVALO_REFRESCO_MS, generacion);
      return;
    }

    this.notificar({
      tipo:
        respuesta.tipo === "respuesta" && respuesta.estado === 401
          ? "refresco_rechazado"
          : "refresco_fallido",
    });
  }

  private notificar(evento: EventoSesion): void {
    for (const observador of this.observadores) {
      observador(evento);
    }
  }
}
