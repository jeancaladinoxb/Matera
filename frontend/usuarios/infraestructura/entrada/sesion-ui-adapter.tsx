import { FormEvent, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { IniciarSesionPort } from "../../aplicacion/puertos/entrada/iniciar-sesion-port";
import { CorreoElectronico } from "../../dominio/correo-electronico";
import { ErrorValidacionDominio } from "../../dominio/errores-dominio";
import { ConsultarMateraDelUsuarioPort } from "../../../materas/aplicacion/puertos/entrada/consultar-matera-del-usuario-port";
import { mensajeDeError } from "./mensajes-ui";

interface PropsSesionUIAdapter {
  readonly iniciarSesion: IniciarSesionPort;
  readonly consultarMateraDelUsuario?: ConsultarMateraDelUsuarioPort;
}

export function SesionUIAdapter({
  iniciarSesion,
  consultarMateraDelUsuario,
}: PropsSesionUIAdapter) {
  const navegar = useNavigate();
  const envioEnCurso = useRef(false);
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [correoTocado, setCorreoTocado] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const errorCorreo =
    correoTocado && correo.length > 0
      ? (() => {
          try {
            new CorreoElectronico(correo);
            return "";
          } catch (error) {
            if (error instanceof ErrorValidacionDominio) {
              return error.message;
            }
            throw error;
          }
        })()
      : "";

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (envioEnCurso.current) {
      return;
    }

    envioEnCurso.current = true;
    setCargando(true);
    setError("");

    try {
      const resultado = await iniciarSesion.iniciarSesion({
        correo,
        contrasena,
      });
      if (resultado.estado === "error") {
        setError(mensajeDeError(resultado.error));
        return;
      }
      if (consultarMateraDelUsuario) {
        const consulta = await consultarMateraDelUsuario.consultarMateraDelUsuario();
        if (consulta.estado === "exito") {
          navegar(
            consulta.valor.vinculada ? "/inicio" : "/materas/vincular",
            { replace: true },
          );
          return;
        }
        if (
          consulta.estado === "error" &&
          consulta.error.tipo === "sesion_vencida"
        ) {
          setError("Tu sesión venció. Inicia sesión nuevamente.");
          return;
        }
      }
      navegar("/inicio", { replace: true });
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  }

  return (
    <section className="auth-card" aria-labelledby="login-titulo">
      <p className="eyebrow">Qué bueno verte</p>
      <h1 id="login-titulo">Inicia sesión</h1>
      <p className="intro-copy">
        Continúa cuidando tus plantas y disfrutando tu momento.
      </p>

      <form className="auth-form" onSubmit={enviarFormulario}>
        <label className="form-field">
          <span>Correo electrónico</span>
          <input
            aria-describedby={errorCorreo ? "login-correo-error" : undefined}
            aria-invalid={Boolean(errorCorreo)}
            autoComplete="email"
            name="correo"
            onBlur={() => setCorreoTocado(true)}
            onChange={(evento) => setCorreo(evento.target.value)}
            required
            type="email"
            value={correo}
          />
          {errorCorreo && (
            <span
              aria-live="polite"
              className="field-error"
              id="login-correo-error"
            >
              {errorCorreo}
            </span>
          )}
        </label>

        <label className="form-field">
          <span>Contraseña</span>
          <input
            autoComplete="current-password"
            name="contrasena"
            onChange={(evento) => setContrasena(evento.target.value)}
            required
            type="password"
            value={contrasena}
          />
        </label>

        {error && (
          <p className="form-error" role="alert" aria-live="assertive">
            {error}
          </p>
        )}

        <button className="primary-button" disabled={cargando} type="submit">
          {cargando ? (
            <>
              <span className="loading-orbit" aria-hidden="true" />
              <span role="status" aria-live="polite">
                Iniciando sesión…
              </span>
            </>
          ) : (
            "Entrar"
          )}
        </button>
      </form>

      <p className="auth-switch">
        ¿Aún no tienes cuenta? <Link to="/registro">Crea una cuenta</Link>
      </p>
    </section>
  );
}
