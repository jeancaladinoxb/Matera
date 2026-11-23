import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { ComposicionUsuarios } from "../composicion/composicion-root";
import { EventoSesion } from "../salida/session-http-adapter";
import { PantallaPrincipal } from "./pantalla-principal";
import { RegistroUIAdapter } from "./registro-ui-adapter";
import { SesionUIAdapter } from "./sesion-ui-adapter";

interface PropsApp {
  readonly composicion: ComposicionUsuarios;
}

function mensajeDeEventoSesion(evento: EventoSesion): string {
  if (evento.tipo === "refresco_rechazado") {
    return "El servidor rechazó la renovación de la sesión. No la cerraremos automáticamente; revisa el estado antes de continuar.";
  }
  return "No pudimos completar la renovación de la sesión. Tu sesión no se cerró automáticamente.";
}

export function App({ composicion }: PropsApp) {
  const [avisoSesion, setAvisoSesion] = useState("");

  useEffect(() => {
    const dejarDeObservar = composicion.sessionHttp.observarEventos((evento) => {
      setAvisoSesion(mensajeDeEventoSesion(evento));
    });

    return () => {
      dejarDeObservar();
      composicion.sessionHttp.desmontar();
    };
  }, [composicion]);

  return (
    <BrowserRouter>
      <main className="app-shell">
        <div className="ambient-orb ambient-orb-one" aria-hidden="true" />
        <div className="ambient-orb ambient-orb-two" aria-hidden="true" />
        <header className="brand-lockup" aria-label="Cuida tu mate">
          <span className="brand-mark" aria-hidden="true">
            <span />
          </span>
          <span>Cuida tu mate</span>
        </header>

        {avisoSesion && (
          <div className="session-notice" role="alert" aria-live="assertive">
            <p>{avisoSesion}</p>
            <button
              aria-label="Cerrar aviso de sesión"
              onClick={() => setAvisoSesion("")}
              type="button"
            >
              Cerrar
            </button>
          </div>
        )}

        <Routes>
          <Route
            element={
              <RegistroUIAdapter
                registrar={composicion.registrarUsuario}
              />
            }
            path="/registro"
          />
          <Route
            element={<SesionUIAdapter iniciarSesion={composicion.iniciarSesion} />}
            path="/login"
          />
          <Route
            element={
              <PantallaPrincipal cerrarSesion={composicion.cerrarSesion} />
            }
            path="/inicio"
          />
          <Route element={<Navigate replace to="/login" />} path="/" />
          <Route element={<Navigate replace to="/login" />} path="*" />
        </Routes>
        <footer className="app-footer">Cultiva bienestar, un mate a la vez.</footer>
      </main>
    </BrowserRouter>
  );
}
