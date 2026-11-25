import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ErrorAplicacion } from "../../../usuarios/aplicacion/errores-aplicacion";
import { mensajeDeError } from "../../../usuarios/infraestructura/entrada/mensajes-ui";
import { ConsultarLogrosPort } from "../../aplicacion/puertos/entrada/consultar-logros-port";
import { Logro } from "../../dominio/logro";
import { PerfilGamificacion } from "../../dominio/perfil-gamificacion";

import "./logros.css";

type EstadoLogros =
  | { readonly tipo: "cargando" }
  | { readonly tipo: "perfil"; readonly valor: PerfilGamificacion }
  | { readonly tipo: "error"; readonly error: ErrorAplicacion };

interface PropsLogrosUIAdapter {
  readonly consultarLogros: ConsultarLogrosPort;
}

const formatoFecha = new Intl.DateTimeFormat("es-CO", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

export function LogrosUIAdapter({ consultarLogros }: PropsLogrosUIAdapter) {
  const navegar = useNavigate();
  const [intento, setIntento] = useState(0);
  const [estado, setEstado] = useState<EstadoLogros>({ tipo: "cargando" });

  useEffect(() => {
    let activo = true;
    void consultarLogros
      .consultarLogros()
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
        setEstado({ tipo: "perfil", valor: resultado.valor });
      })
      .catch(() => {
        if (activo) setEstado({ tipo: "error", error: { tipo: "desconocido" } });
      });

    return () => {
      activo = false;
    };
  }, [consultarLogros, intento, navegar]);

  if (estado.tipo === "cargando") {
    return (
      <p aria-live="polite" className="logros-estado" role="status">
        <span aria-hidden="true" className="loading-orbit" />
        Cargando tus logros…
      </p>
    );
  }

  if (estado.tipo === "error") {
    return (
      <div className="logros-estado">
        <p className="form-error" role="alert">
          {mensajeDeError(estado.error)}
        </p>
        <button
          className="secondary-button"
          onClick={() => {
            setEstado({ tipo: "cargando" });
            setIntento((actual) => actual + 1);
          }}
          type="button"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const perfil = estado.valor;
  return (
    <div className="logros-contenido">
      <div className="logros-nivel">
        <div>
          <p className="eyebrow">Nivel {perfil.nivel.numero}</p>
          <p className="logros-nivel-nombre">{perfil.nivel.nombre}</p>
        </div>
        <p className="logros-puntos">
          <strong>{perfil.puntos}</strong> pts
        </p>
        <div
          aria-label="Progreso hacia el siguiente nivel"
          aria-valuemax={100}
          aria-valuemin={0}
          aria-valuenow={perfil.porcentajeNivel}
          className="logros-barra"
          role="progressbar"
        >
          <span style={{ width: `${perfil.porcentajeNivel}%` }} />
        </div>
        <p className="logros-siguiente">
          {perfil.siguienteNivel === null
            ? "¡Llegaste al nivel máximo!"
            : `Te faltan ${perfil.puntosParaSiguienteNivel} pts para ${perfil.siguienteNivel.nombre}`}
        </p>
      </div>

      <p className="logros-resumen">
        {perfil.logrosDesbloqueados} de {perfil.logros.length} logros desbloqueados
      </p>
      <ul className="logros-lista">
        {perfil.logros.map((logro) => (
          <TarjetaLogro key={logro.codigo} logro={logro} />
        ))}
      </ul>
    </div>
  );
}

function TarjetaLogro({ logro }: { readonly logro: Logro }) {
  return (
    <li
      className={`logro-tarjeta ${logro.desbloqueado ? "logro-desbloqueado" : "logro-bloqueado"}`}
    >
      <span aria-hidden="true" className="logro-icono">
        {logro.icono}
      </span>
      <div className="logro-texto">
        <h3>
          {logro.nombre}
          <span className="visually-hidden">
            {logro.desbloqueado ? " (desbloqueado)" : " (bloqueado)"}
          </span>
        </h3>
        <p>{logro.descripcion}</p>
        {logro.desbloqueado && logro.fechaDesbloqueo ? (
          <p className="logro-meta">
            +{logro.puntos} pts · {formatoFecha.format(logro.fechaDesbloqueo)}
          </p>
        ) : (
          <p className="logro-meta">
            {logro.progreso}/{logro.meta} · {logro.puntos} pts
          </p>
        )}
      </div>
    </li>
  );
}
