import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { RegistrarUsuarioPort } from "../../aplicacion/puertos/entrada/registrar-usuario-port";
import { CorreoElectronico } from "../../dominio/correo-electronico";
import { ContraseñaDeRegistro } from "../../dominio/contrasena-de-registro";
import { ErrorValidacionDominio } from "../../dominio/errores-dominio";
import { mensajeDeError } from "./mensajes-ui";

interface PropsRegistroUIAdapter {
  readonly registrar: RegistrarUsuarioPort;
}

function mensajeDeValidacion<T>(crear: () => T): string {
  try {
    crear();
    return "";
  } catch (error) {
    if (error instanceof ErrorValidacionDominio) {
      return error.message;
    }
    throw error;
  }
}

export function RegistroUIAdapter({ registrar }: PropsRegistroUIAdapter) {
  const navegar = useNavigate();
  const envioEnCurso = useRef(false);
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [nickname, setNickname] = useState("");
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [correoTocado, setCorreoTocado] = useState(false);
  const [contrasenaTocada, setContrasenaTocada] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [registroExitoso, setRegistroExitoso] = useState(false);

  const errorCorreo = correoTocado
    ? mensajeDeValidacion(() => new CorreoElectronico(correo))
    : "";
  const errorContrasena = contrasenaTocada
    ? mensajeDeValidacion(() => new ContraseñaDeRegistro(contrasena))
    : "";

  useEffect(() => {
    if (!registroExitoso) {
      return;
    }
    const temporizador = window.setTimeout(
      () => navegar("/login", { replace: true }),
      3000,
    );
    return () => window.clearTimeout(temporizador);
  }, [navegar, registroExitoso]);

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (envioEnCurso.current) {
      return;
    }

    envioEnCurso.current = true;
    setCargando(true);
    setError("");

    try {
      const resultado = await registrar.registrarUsuario({
        nombre,
        apellido,
        nickname,
        correo,
        contrasena,
      });
      if (resultado.estado === "error") {
        setError(mensajeDeError(resultado.error));
        return;
      }
      setRegistroExitoso(true);
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  }

  if (registroExitoso) {
    return (
      <section className="auth-card success-card" aria-labelledby="registro-titulo">
        <div className="success-mark" aria-hidden="true">
          ✓
        </div>
        <p className="eyebrow">Todo listo</p>
        <h1 id="registro-titulo">Registro exitoso</h1>
        <p role="status" aria-live="polite">
          En un momento te llevaremos al inicio de sesión.
        </p>
        <Link className="text-link" to="/login" replace>
          Ir ahora a iniciar sesión
        </Link>
      </section>
    );
  }

  return (
    <section className="auth-card" aria-labelledby="registro-titulo">
      <p className="eyebrow">Una rutina más consciente</p>
      <h1 id="registro-titulo">Crea tu cuenta</h1>
      <p className="intro-copy">
        Empieza a cuidar tus plantas y a disfrutar cada mate.
      </p>

      <form className="auth-form" onSubmit={enviarFormulario}>
        <div className="field-row">
          <label className="form-field">
            <span>Nombre</span>
            <input
              autoComplete="given-name"
              name="nombre"
              onChange={(evento) => setNombre(evento.target.value)}
              required
              value={nombre}
            />
          </label>
          <label className="form-field">
            <span>Apellido</span>
            <input
              autoComplete="family-name"
              name="apellido"
              onChange={(evento) => setApellido(evento.target.value)}
              required
              value={apellido}
            />
          </label>
        </div>

        <label className="form-field">
          <span>Nickname</span>
          <input
            autoComplete="nickname"
            name="nickname"
            onChange={(evento) => setNickname(evento.target.value)}
            required
            value={nickname}
          />
        </label>

        <label className="form-field">
          <span>Correo electrónico</span>
          <input
            aria-describedby={errorCorreo ? "registro-correo-error" : undefined}
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
              id="registro-correo-error"
            >
              {errorCorreo}
            </span>
          )}
        </label>

        <label className="form-field">
          <span>Contraseña</span>
          <input
            aria-describedby={
              errorContrasena ? "registro-contrasena-error" : "registro-ayuda"
            }
            aria-invalid={Boolean(errorContrasena)}
            autoComplete="new-password"
            name="contrasena"
            onBlur={() => setContrasenaTocada(true)}
            onChange={(evento) => setContrasena(evento.target.value)}
            required
            type="password"
            value={contrasena}
          />
          {errorContrasena ? (
            <span
              aria-live="polite"
              className="field-error"
              id="registro-contrasena-error"
            >
              {errorContrasena}
            </span>
          ) : (
            <span className="field-hint" id="registro-ayuda">
              8 caracteres o más, solo letras y números, con una mayúscula.
            </span>
          )}
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
                Creando tu cuenta…
              </span>
            </>
          ) : (
            "Crear cuenta"
          )}
        </button>
      </form>

      <p className="auth-switch">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </section>
  );
}
