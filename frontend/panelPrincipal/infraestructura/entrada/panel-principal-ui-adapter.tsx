import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ConsultarPanelPrincipalPort } from "../../aplicacion/puertos/entrada/consultar-panel-principal-port";
import { ErrorAplicacion } from "../../../usuarios/aplicacion/errores-aplicacion";
import { ResultadoAplicacion } from "../../../usuarios/aplicacion/resultado-aplicacion";
import { mensajeDeError } from "../../../usuarios/infraestructura/entrada/mensajes-ui";
import { PanelPrincipal } from "../../dominio/panel-principal";

import "./panel-principal.css";

type EstadoPantalla =
  | { readonly tipo: "cargando" }
  | { readonly tipo: "panel"; readonly valor: PanelPrincipal }
  | { readonly tipo: "error"; readonly error: ErrorAplicacion };

interface SolicitudPanel {
  readonly intento: number;
  readonly promesa: Promise<ResultadoAplicacion<PanelPrincipal>>;
}

interface PropsPanelPrincipalUIAdapter {
  readonly consultarPanel: ConsultarPanelPrincipalPort;
}

export function PanelPrincipalUIAdapter({
  consultarPanel,
}: PropsPanelPrincipalUIAdapter) {
  const navegar = useNavigate();
  const solicitud = useRef<SolicitudPanel | null>(null);
  const [intento, setIntento] = useState(0);
  const [estado, setEstado] = useState<EstadoPantalla>({ tipo: "cargando" });
  const [avisoPlantaId, setAvisoPlantaId] = useState<number | null>(null);
  const [avisoGamificacion, setAvisoGamificacion] = useState(false);

  useEffect(() => {
    let activo = true;
    let actual = solicitud.current;
    if (!actual || actual.intento !== intento) {
      actual = {
        intento,
        promesa: consultarPanel.consultarPanelPrincipal(),
      };
      solicitud.current = actual;
    }

    void actual.promesa
      .then((resultado) => {
        if (!activo) return;
        if (resultado.estado === "error") {
          if (resultado.error.tipo === "sesion_vencida") {
            navegar("/login", { replace: true });
            return;
          }
          setEstado({ tipo: "error", error: resultado.error });
          return;
        }

        if (resultado.valor.materas.length === 0) {
          navegar("/materas/vincular", { replace: true });
          return;
        }
        setEstado({ tipo: "panel", valor: resultado.valor });
      })
      .catch(() => {
        if (activo) {
          setEstado({ tipo: "error", error: { tipo: "desconocido" } });
        }
      });

    return () => {
      activo = false;
    };
  }, [consultarPanel, intento, navegar]);

  function reintentar() {
    solicitud.current = null;
    setEstado({ tipo: "cargando" });
    setIntento((actual) => actual + 1);
  }

  if (estado.tipo === "cargando") {
    return (
      <div
        aria-labelledby="panel-cargando-titulo"
        aria-live="polite"
        className="panel-loading-state"
      >
        <p className="eyebrow">Cuida tu mate</p>
        <h1 id="panel-cargando-titulo">Preparando tu panel</h1>
        <p role="status">
          <span aria-hidden="true" className="loading-orbit" />
          Cargando tus materas…
        </p>
      </div>
    );
  }

  if (estado.tipo === "error") {
    return (
      <div
        aria-labelledby="panel-error-titulo"
        className="panel-error-state"
      >
        <p className="eyebrow">Cuida tu mate</p>
        <h1 id="panel-error-titulo">No pudimos cargar tu panel</h1>
        <p aria-live="assertive" className="form-error" role="alert">
          {mensajeDeError(estado.error)}
        </p>
        <button
          className="primary-button"
          onClick={reintentar}
          type="button"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="panel-content">
      <header className="panel-heading">
        <p className="eyebrow">Tu espacio para crecer</p>
        <h1 id="panel-titulo">Hola, {estado.valor.usuario.nickname}</h1>
        <p className="intro-copy">
          Tu cuenta de usuario es #{estado.valor.usuario.usuarioId}.
        </p>
      </header>

      <section aria-labelledby="materas-titulo" className="panel-section">
        <h2 id="materas-titulo">Tus materas</h2>
        <ul className="panel-matera-list">
          {estado.valor.materas.map((matera) => (
            <li className="panel-matera-card" key={matera.materaId}>
              <h3>Matera #{matera.materaId}</h3>
              <p>MAC: {matera.mac}</p>
              <p>
                {matera.plantaId === null
                  ? "Sin planta asignada"
                  : `Planta asignada #${matera.plantaId}`}
              </p>
              {matera.sugerirVincularPlanta && (
                <div>
                  <button
                    className="secondary-button"
                    onClick={() => setAvisoPlantaId(matera.materaId)}
                    type="button"
                  >
                    Vincular una planta
                  </button>
                  {avisoPlantaId === matera.materaId && (
                    <p aria-live="polite" role="status">
                      La vinculación de plantas estará disponible muy pronto.
                    </p>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      </section>

      {estado.valor.tieneOpcionGamificacion && (
        <section aria-labelledby="gamificacion-titulo" className="panel-section">
          <h2 id="gamificacion-titulo">Gamificación</h2>
          <button
            className="secondary-button"
            onClick={() => setAvisoGamificacion(true)}
            type="button"
          >
            Explorar gamificación
          </button>
          {avisoGamificacion && (
            <p aria-live="polite" role="status">
              La gamificación no está disponible por ahora.
            </p>
          )}
        </section>
      )}
    </div>
  );
}
