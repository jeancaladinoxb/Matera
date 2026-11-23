import { FormEvent, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { CerrarSesionPort } from "../../aplicacion/puertos/entrada/cerrar-sesion-port";
import { mensajeDeError } from "./mensajes-ui";

interface PropsPantallaPrincipal {
  readonly cerrarSesion: CerrarSesionPort;
}

export function PantallaPrincipal({
  cerrarSesion,
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
    <section className="auth-card home-card" aria-labelledby="inicio-titulo">
      <p className="eyebrow">Cuida tu mate</p>
      <h1 id="inicio-titulo">Tu espacio para crecer</h1>
      <p className="intro-copy">
        Tu sesión está activa. Muy pronto encontrarás aquí el cuidado de tus
        plantas.
      </p>
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
  );
}
