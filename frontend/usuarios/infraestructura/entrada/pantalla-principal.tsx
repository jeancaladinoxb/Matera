import { FormEvent, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { CerrarSesionPort } from "../../aplicacion/puertos/entrada/cerrar-sesion-port";
import { mensajeDeError } from "./mensajes-ui";
import { ConsultarPanelPrincipalPort } from "../../../panelPrincipal/aplicacion/puertos/entrada/consultar-panel-principal-port";
import { PanelPrincipalUIAdapter } from "../../../panelPrincipal/infraestructura/entrada/panel-principal-ui-adapter";

interface PropsPantallaPrincipal {
  readonly cerrarSesion: CerrarSesionPort;
  readonly consultarPanel: ConsultarPanelPrincipalPort;
}

export function PantallaPrincipal({
  cerrarSesion,
  consultarPanel,
}: PropsPantallaPrincipal) {
  const navegar = useNavigate();
  const envioEnCurso = useRef(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  async function salir(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (envioEnCurso.current) {
      return;
    }

    envioEnCurso.current = true;
    setCargando(true);
    setError("");
    try {
      const resultado = await cerrarSesion.cerrarSesion();
      if (resultado.estado === "error") {
        setError(mensajeDeError(resultado.error));
        return;
      }
      navegar("/login", { replace: true });
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  }

  return (
    <section
      aria-label="Panel principal"
      className="auth-card home-card panel-home-card"
    >
      <PanelPrincipalUIAdapter consultarPanel={consultarPanel} />
      <section
        aria-labelledby="panel-sesion-titulo"
        className="panel-session-actions"
      >
        <h2 id="panel-sesion-titulo">Tu sesión</h2>
        {error && (
          <p className="form-error" role="alert" aria-live="assertive">
            {error}
          </p>
        )}
        <form onSubmit={salir}>
          <button className="secondary-button" disabled={cargando} type="submit">
            {cargando ? "Cerrando sesión…" : "Cerrar sesión"}
          </button>
        </form>
      </section>
    </section>
  );
}
