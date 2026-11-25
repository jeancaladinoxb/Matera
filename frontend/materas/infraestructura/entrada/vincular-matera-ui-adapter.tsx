import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { VincularMateraPort } from "../../aplicacion/puertos/entrada/vincular-matera-port";
import { VincularMateraDesdeQrPort } from "../../aplicacion/puertos/entrada/vincular-matera-desde-qr-port";
import { DireccionMac } from "../../dominio/direccion-mac";
import { CodigoDeVinculacion } from "../../dominio/codigo-de-vinculacion";
import { ErrorValidacionMatera } from "../../dominio/errores-dominio";
import { mensajeDeError } from "../../../usuarios/infraestructura/entrada/mensajes-ui";
import { CamaraQrAdapter, ErrorCamaraQr } from "./camara-qr-adapter";

interface PropsVincularMateraUIAdapter {
  readonly vincularMatera: VincularMateraPort;
  readonly vincularDesdeQr: VincularMateraDesdeQrPort;
}

function mensajeCamara(error: ErrorCamaraQr): string {
  switch (error) {
    case "permiso_denegado":
      return "Necesitamos permiso para usar la cámara. Puedes ingresar los datos manualmente.";
    case "sin_camara":
      return "No encontramos una cámara disponible. Puedes ingresar los datos manualmente.";
    case "contexto_inseguro":
      return "La cámara requiere HTTPS o localhost. Puedes usar el modo manual o abrir la app con una conexión segura.";
    case "error_desconocido":
      return "No pudimos iniciar la cámara. Puedes ingresar los datos manualmente.";
  }
}

export function VincularMateraUIAdapter({
  vincularMatera,
  vincularDesdeQr,
}: PropsVincularMateraUIAdapter) {
  const navegar = useNavigate();
  const envioEnCurso = useRef(false);
  const camara = useRef(new CamaraQrAdapter());
  const entradaFoto = useRef<HTMLInputElement>(null);
  const [modo, setModo] = useState<"camara" | "manual">("camara");
  const [mac, setMac] = useState("");
  const [codigo, setCodigo] = useState("");
  const [macTocada, setMacTocada] = useState(false);
  const [codigoTocado, setCodigoTocado] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [exito, setExito] = useState(false);

  function validarMac(): string {
    if (!macTocada) return "";
    try {
      new DireccionMac(mac);
      return "";
    } catch (error) {
      return error instanceof ErrorValidacionMatera
        ? error.message
        : "La MAC no tiene un formato válido.";
    }
  }

  function validarCodigo(): string {
    if (!codigoTocado) return "";
    try {
      new CodigoDeVinculacion(codigo);
      return "";
    } catch (error) {
      return error instanceof ErrorValidacionMatera
        ? error.message
        : "El código de vinculación no tiene un formato válido.";
    }
  }

  const errorMac = validarMac();
  const errorCodigo = validarCodigo();

  useEffect(() => {
    if (!exito) return;
    const temporizador = window.setTimeout(
      () => navegar("/inicio", { replace: true }),
      3000,
    );
    return () => window.clearTimeout(temporizador);
  }, [exito, navegar]);

  useEffect(() => {
    if (modo !== "camara") return;

    let activo = true;
    void Promise.resolve().then(() => {
      if (activo) return iniciarCamara(() => activo);
    });

    return () => {
      activo = false;
      void camara.current.detener().catch(() => undefined);
    };
  }, [modo]);

  async function iniciarCamara(estaActivo: () => boolean) {
    setError("");
    const problema = await camara.current.iniciar(
      "matera-qr-lector",
      (textoQr) => {
        if (estaActivo()) void enviarQr(async () => textoQr);
      },
    );
    if (problema && estaActivo()) {
      setError(mensajeCamara(problema));
    }
  }

  async function enviarQr(leer: () => Promise<string>) {
    if (envioEnCurso.current) return;
    envioEnCurso.current = true;
    setCargando(true);
    setError("");

    try {
      await camara.current.detener().catch(() => undefined);

      let textoQr: string;
      try {
        textoQr = await leer();
      } catch {
        setError(
          "No pudimos leer el QR. Mantén el código completo y enfocado dentro del recuadro, o prueba con una foto.",
        );
        return;
      }

      try {
        const resultado = await vincularDesdeQr.vincularDesdeQr(textoQr);
        if (resultado.estado === "error") {
          setError(mensajeDeError(resultado.error));
          setModo("manual");
          return;
        }
        setExito(true);
      } catch {
        setError(
          "El QR se leyó, pero no pudimos completar la vinculación. Revisa tu conexión o ingresa los datos manualmente.",
        );
      }
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  }

  async function enviarManual(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (envioEnCurso.current) return;

    envioEnCurso.current = true;
    setCargando(true);
    setError("");

    try {
      const resultado = await vincularMatera.vincular({ mac, codigo });
      if (resultado.estado === "error") {
        setError(mensajeDeError(resultado.error));
        return;
      }
      setCodigo("");
      setExito(true);
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  }

  async function mostrarModoManual() {
    await camara.current.detener();
    setModo("manual");
  }

  if (exito) {
    return (
      <section className="auth-card success-card" aria-labelledby="matera-exito">
        <div className="success-mark" aria-hidden="true">✓</div>
        <p className="eyebrow">Todo listo</p>
        <h1 id="matera-exito">Matera vinculada</h1>
        <p role="status" aria-live="polite">
          Ya puedes continuar al panel principal.
        </p>
      </section>
    );
  }

  return (
    <section className="auth-card" aria-labelledby="vincular-titulo">
      <p className="eyebrow">Tu primer paso</p>
      <h1 id="vincular-titulo">Vincula tu matera</h1>
      <p className="intro-copy">
        Escanea el QR que viene con tu matera.
      </p>

      {modo === "camara" && (
        <p className="field-hint">
          Mantén el QR completo visible en el visor. Se leerá automáticamente
          cuando la cámara lo enfoque.
        </p>
      )}

      <div className="matera-mode-tabs" aria-label="Método de vinculación">
        <button
          aria-pressed={modo === "camara"}
          className={modo === "camara" ? "secondary-button is-active" : "secondary-button"}
          onClick={() => setModo("camara")}
          type="button"
        >
          Cámara
        </button>
        <button
          aria-pressed={modo === "manual"}
          className={modo === "manual" ? "secondary-button is-active" : "secondary-button"}
          onClick={() => void mostrarModoManual()}
          type="button"
        >
          Ingresar datos
        </button>
      </div>

      {modo === "camara" ? (
        <div className="matera-camera-section">
          <div
            aria-label="Visor de cámara para escanear el código QR"
            className="matera-camera"
            id="matera-qr-lector"
          />
          <div hidden id="matera-qr-foto" />
          <input
            accept="image/*"
            capture="environment"
            hidden
            onChange={(evento) => {
              const foto = evento.currentTarget.files?.[0];
              evento.currentTarget.value = "";
              if (foto) {
                void enviarQr(() => camara.current.leerFoto("matera-qr-foto", foto));
              }
            }}
            ref={entradaFoto}
            type="file"
          />
          <button
            className="secondary-button"
            disabled={cargando}
            onClick={() => entradaFoto.current?.click()}
            type="button"
          >
            {cargando ? "Leyendo QR…" : "Probar con una foto"}
          </button>
          <button
            className="text-link matera-manual-link"
            onClick={() => void mostrarModoManual()}
            type="button"
          >
            Usar MAC y código manualmente
          </button>
        </div>
      ) : (
        <form className="auth-form" onSubmit={enviarManual}>
          <label className="form-field">
            <span>Dirección MAC</span>
            <input
              aria-describedby={errorMac ? "matera-mac-error" : undefined}
              aria-invalid={Boolean(errorMac)}
              onBlur={() => setMacTocada(true)}
              onChange={(evento) => setMac(evento.target.value)}
              placeholder="24:6F:28:AB:12:34"
              value={mac}
            />
            {errorMac && (
              <span aria-live="polite" className="field-error" id="matera-mac-error">
                {errorMac}
              </span>
            )}
          </label>

          <label className="form-field">
            <span>Código de vinculación</span>
            <input
              aria-describedby={errorCodigo ? "matera-codigo-error" : undefined}
              aria-invalid={Boolean(errorCodigo)}
              autoComplete="off"
              onBlur={() => setCodigoTocado(true)}
              onChange={(evento) => setCodigo(evento.target.value)}
              placeholder="12 caracteres"
              type="password"
              value={codigo}
            />
            {errorCodigo && (
              <span aria-live="polite" className="field-error" id="matera-codigo-error">
                {errorCodigo}
              </span>
            )}
          </label>

          {error && (
            <p aria-live="assertive" className="form-error" role="alert">
              {error}
            </p>
          )}

          <button className="primary-button" disabled={cargando} type="submit">
            {cargando ? (
              <>
                <span className="loading-orbit" aria-hidden="true" />
                <span role="status" aria-live="polite">Vinculando…</span>
              </>
            ) : (
              "Vincular matera"
            )}
          </button>
        </form>
      )}

      {modo === "camara" && error && (
        <p aria-live="assertive" className="form-error" role="alert">
          {error}
        </p>
      )}

      <p className="auth-switch">
        <Link to="/inicio">Más tarde</Link>
      </p>
    </section>
  );
}
