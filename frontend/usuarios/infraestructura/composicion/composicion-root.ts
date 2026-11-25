import { RegistrarUsuarioUseCase } from "../../aplicacion/casos-de-uso/registrar-usuario-use-case";
import { IniciarSesionUseCase } from "../../aplicacion/casos-de-uso/iniciar-sesion-use-case";
import { CerrarSesionUseCase } from "../../aplicacion/casos-de-uso/cerrar-sesion-use-case";
import { RegistroHttpAdapter } from "../salida/registro-http-adapter";
import { SessionHttpAdapter } from "../salida/session-http-adapter";
import { ClienteHttp } from "../salida/cliente-http";
import { VincularMateraUseCase } from "../../../materas/aplicacion/casos-de-uso/vincular-matera-use-case";
import { VincularMateraDesdeQrUseCase } from "../../../materas/aplicacion/casos-de-uso/vincular-matera-desde-qr-use-case";
import { ConsultarMateraDelUsuarioUseCase } from "../../../materas/aplicacion/casos-de-uso/consultar-matera-del-usuario-use-case";
import { MateraHttpAdapter } from "../../../materas/infraestructura/salida/matera-http-adapter";
import { ConsultarPanelPrincipalUseCase } from "../../../panelPrincipal/aplicacion/casos-de-uso/consultar-panel-principal-use-case";
import { ConsultarLogrosUseCase } from "../../../gamificacion/aplicacion/casos-de-uso/consultar-logros-use-case";
import { LogrosHttpAdapter } from "../../../gamificacion/infraestructura/salida/logros-http-adapter";
import { UsuarioMateraHttpAdapter } from "../../../panelPrincipal/infraestructura/salida/usuario-matera-http-adapter";
import { ListarPlantasUseCase } from "../../../plantas/aplicacion/casos-de-uso/listar-plantas-use-case";
import { VincularPlantaUseCase } from "../../../plantas/aplicacion/casos-de-uso/vincular-planta-use-case";
import { PlantaHttpAdapter } from "../../../plantas/infraestructura/salida/planta-http-adapter";

export function crearComposicionUsuarios() {
  const clienteHttp = new ClienteHttp();
  const registroHttp = new RegistroHttpAdapter(clienteHttp);
  const sessionHttp = new SessionHttpAdapter(clienteHttp);
  const materaHttp = new MateraHttpAdapter(clienteHttp);
  const panelHttp = new UsuarioMateraHttpAdapter(clienteHttp);
  const logrosHttp = new LogrosHttpAdapter(clienteHttp);
  const plantaHttp = new PlantaHttpAdapter(clienteHttp);
  const vincularMatera = new VincularMateraUseCase(materaHttp);

  return {
    registrarUsuario: new RegistrarUsuarioUseCase(registroHttp),
    iniciarSesion: new IniciarSesionUseCase(sessionHttp),
    cerrarSesion: new CerrarSesionUseCase(sessionHttp),
    sessionHttp,
    vincularMatera,
    vincularMateraDesdeQr: new VincularMateraDesdeQrUseCase(vincularMatera),
    consultarMateraDelUsuario:
      new ConsultarMateraDelUsuarioUseCase(materaHttp),
    consultarPanelPrincipal: new ConsultarPanelPrincipalUseCase(panelHttp),
    consultarLogros: new ConsultarLogrosUseCase(logrosHttp),
    listarPlantas: new ListarPlantasUseCase(plantaHttp),
    vincularPlanta: new VincularPlantaUseCase(plantaHttp),
  };
}

export type ComposicionUsuarios = ReturnType<typeof crearComposicionUsuarios>;
