import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ConsultarPanelPrincipalPort } from "../../../panelPrincipal/aplicacion/puertos/entrada/consultar-panel-principal-port";
import { Matera } from "../../../panelPrincipal/dominio/matera";
import { ErrorAplicacion } from "../../../usuarios/aplicacion/errores-aplicacion";
import { mensajeDeError } from "../../../usuarios/infraestructura/entrada/mensajes-ui";
import { ListarPlantasPort } from "../../aplicacion/puertos/entrada/listar-plantas-port";
import { VincularPlantaPort } from "../../aplicacion/puertos/entrada/vincular-planta-port";
import { Planta } from "../../dominio/planta";
import { IlustracionPlanta } from "./ilustraciones-plantas";
import {
  etiquetaMatera,
  filtrarPlantas,
  textoLuz,
  textoRiego,
} from "./presentacion-plantas";

import "./plantas.css";

interface PropsPlantasUIAdapter {
  readonly consultarPanel: ConsultarPanelPrincipalPort;
  readonly listarPlantas: ListarPlantasPort;
  readonly vincularPlanta: VincularPlantaPort;
}

type EstadoPantalla =
  | { readonly tipo: "cargando" }
  | { readonly tipo: "error"; readonly error: ErrorAplicacion }
  | { readonly tipo: "matera_no_encontrada" }
  | {
      readonly tipo: "listo";
      readonly plantas: readonly Planta[];
      readonly matera: Matera;
    };

// El identificador viene de la URL: solo se acepta un entero positivo escrito en decimal.
function leerMateraId(texto: string | undefined): number | null {
  if (texto === undefined || !/^[1-9]\d*$/.test(texto)) {
    return null;
  }
  const valor = Number(texto);
  return Number.isSafeInteger(valor) ? valor : null;
}

function Encabezado() {
  return (
    <>
      <Link className="secondary-button plantas-volver" to="/inicio">
        ← Volver al panel
      </Link>
      <header className="plantas-encabezado">
        <p className="eyebrow">Cuida tu mate</p>
        <h1 id="plantas-titulo">¿Qué planta vas a cuidar?</h1>
        <p className="intro-copy">
          Elige la especie para tu matera. Puedes cambiarla cuando quieras.
        </p>
      </header>
    </>
  );
}

export function PlantasUIAdapter({
  consultarPanel,
  listarPlantas,
  vincularPlanta,
}: PropsPlantasUIAdapter) {
  const navegar = useNavigate();
  const { materaId: materaIdUrl } = useParams();
  const materaId = leerMateraId(materaIdUrl);
  const envioEnCurso = useRef(false);
  const [intento, setIntento] = useState(0);
  const [estado, setEstado] = useState<EstadoPantalla>({ tipo: "cargando" });
  const [busqueda, setBusqueda] = useState("");
  const [seleccion, setSeleccion] = useState<number | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [errorVincular, setErrorVincular] = useState("");

  useEffect(() => {
    if (materaId === null) {
      return;
    }

    let activo = true;
    function fallar(error: ErrorAplicacion) {
      if (error.tipo === "sesion_vencida") {
        navegar("/login", { replace: true });
        return;
      }
      setEstado({ tipo: "error", error });
    }

    void Promise.all([
      consultarPanel.consultarPanelPrincipal(),
      listarPlantas.listarPlantas(),
    ])
      .then(([panel, plantas]) => {
        if (!activo) return;
        if (panel.estado === "error") return fallar(panel.error);
        if (plantas.estado === "error") return fallar(plantas.error);

        const matera = panel.valor.materas.find(
          (candidata) => candidata.materaId === materaId,
        );
        if (!matera) {
          setEstado({ tipo: "matera_no_encontrada" });
          return;
        }

        // Si la matera ya tiene planta, esa tarjeta aparece preseleccionada
        const actual = plantas.valor.find((planta) => planta.id === matera.plantaId);
        setSeleccion(actual ? actual.id : null);
        setEstado({ tipo: "listo", plantas: plantas.valor, matera });
      })
      .catch(() => {
        if (activo) {
          setEstado({ tipo: "error", error: { tipo: "desconocido" } });
        }
      });

    return () => {
      activo = false;
    };
  }, [consultarPanel, listarPlantas, intento, materaId, navegar]);

  function reintentar() {
    setEstado({ tipo: "cargando" });
    setIntento((actual) => actual + 1);
  }

  async function vincular(plantaId: number) {
    if (materaId === null || envioEnCurso.current) {
      return;
    }

    envioEnCurso.current = true;
    setEnviando(true);
    setErrorVincular("");
    try {
      const resultado = await vincularPlanta.vincularPlanta({ materaId, plantaId });
      if (resultado.estado === "error") {
        if (resultado.error.tipo === "sesion_vencida") {
          navegar("/login", { replace: true });
          return;
        }
        setErrorVincular(mensajeDeError(resultado.error));
        return;
      }
      navegar("/inicio", { replace: true });
    } finally {
      envioEnCurso.current = false;
      setEnviando(false);
    }
  }

  if (materaId === null || estado.tipo === "matera_no_encontrada") {
    return (
      <section aria-labelledby="plantas-titulo" className="auth-card plantas-card">
        <Encabezado />
        <div className="plantas-estado">
          <p aria-live="assertive" className="form-error" role="alert">
            {mensajeDeError({ tipo: "no_encontrado" })}
          </p>
        </div>
      </section>
    );
  }

  if (estado.tipo === "cargando") {
    return (
      <section aria-labelledby="plantas-titulo" className="auth-card plantas-card">
        <Encabezado />
        <div aria-live="polite" className="plantas-estado">
          <p role="status">
            <span aria-hidden="true" className="loading-orbit" />
            Cargando plantas…
          </p>
        </div>
      </section>
    );
  }

  if (estado.tipo === "error") {
    return (
      <section aria-labelledby="plantas-titulo" className="auth-card plantas-card">
        <Encabezado />
        <div className="plantas-estado">
          <p aria-live="assertive" className="form-error" role="alert">
            {mensajeDeError(estado.error)}
          </p>
          <button className="primary-button" onClick={reintentar} type="button">
            Reintentar
          </button>
        </div>
      </section>
    );
  }

  const { plantas, matera } = estado;
  const visibles = filtrarPlantas(plantas, busqueda);
  const elegida = plantas.find((planta) => planta.id === seleccion);

  return (
    <section aria-labelledby="plantas-titulo" className="auth-card plantas-card">
      <Encabezado />
      <div className="plantas-layout">
        <div className="plantas-catalogo">
          <label className="form-field">
            <span>Buscar planta</span>
            <input
              autoComplete="off"
              name="busqueda"
              onChange={(evento) => setBusqueda(evento.target.value)}
              placeholder="Monstera, Pothos…"
              type="search"
              value={busqueda}
            />
          </label>

          <p aria-live="polite" className="plantas-cuenta" role="status">
            {visibles.length} de {plantas.length} plantas
          </p>

          {visibles.length === 0 ? (
            <p className="plantas-vacio">No encontramos plantas con ese nombre.</p>
          ) : (
            <fieldset className="plantas-grupo">
              <legend className="plantas-oculto">Plantas disponibles</legend>
              {visibles.map((planta) => (
                <label className="plantas-opcion" key={planta.id}>
                  <input
                    checked={seleccion === planta.id}
                    name="planta"
                    onChange={() => setSeleccion(planta.id)}
                    type="radio"
                    value={planta.id}
                  />
                  <span className="plantas-tarjeta">
                    <span aria-hidden="true" className="plantas-marca">
                      ✓
                    </span>
                    <IlustracionPlanta
                      className="plantas-ilustracion"
                      slug={planta.slug}
                    />
                    <span className="plantas-nombre">{planta.nombreComun}</span>
                    <span className="plantas-cientifico">
                      {planta.nombreCientifico}
                    </span>
                  </span>
                </label>
              ))}
            </fieldset>
          )}
        </div>

        <aside aria-labelledby="plantas-resumen-titulo" className="plantas-resumen">
          <p className="eyebrow" id="plantas-resumen-titulo">
            Vincular con
          </p>
          <IlustracionPlanta
            className="plantas-ilustracion-grande"
            slug={elegida?.slug}
          />
          <p className="plantas-matera">{etiquetaMatera(matera.mac)}</p>
          <p className="plantas-elegida">
            {elegida ? elegida.nombreComun : "Elige una planta"}
          </p>
          <ul className="plantas-chips">
            {elegida && (
              <>
                <li>{textoLuz(elegida)}</li>
                <li>{textoRiego(elegida)}</li>
              </>
            )}
          </ul>
          {errorVincular && (
            <p aria-live="assertive" className="form-error" role="alert">
              {errorVincular}
            </p>
          )}
          <button
            className="primary-button"
            disabled={!elegida || enviando}
            onClick={() => elegida && void vincular(elegida.id)}
            type="button"
          >
            {enviando ? "Vinculando…" : "Vincular planta →"}
          </button>
        </aside>
      </div>
    </section>
  );
}
