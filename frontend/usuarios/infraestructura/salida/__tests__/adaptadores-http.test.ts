import { afterEach, describe, expect, it, vi } from "vitest";

import { ContraseñaDeInicioSesion } from "../../../dominio/contrasena-de-inicio-sesion";
import { ContraseñaDeRegistro } from "../../../dominio/contrasena-de-registro";
import { CorreoElectronico } from "../../../dominio/correo-electronico";
import { Usuario } from "../../../dominio/usuario";
import { ClienteHttp, ClienteHttpPort, ResultadoHttp } from "../cliente-http";
import { RegistroHttpAdapter } from "../registro-http-adapter";
import { SessionHttpAdapter } from "../session-http-adapter";

function respuesta(estado: number, cuerpo: unknown = undefined): ResultadoHttp {
  return { tipo: "respuesta", estado, cuerpo };
}

function usuarioDePrueba(): Usuario {
  return new Usuario({
    nombre: "Ana",
    apellido: "Pérez",
    nickname: "anap",
    correo: new CorreoElectronico(" Ana@Example.COM "),
    contrasena: new ContraseñaDeRegistro("Clave123"),
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("ClienteHttp", () => {
  it("incluye credenciales para que el navegador envíe la cookie HttpOnly", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response('{"mensaje":"ok"}', { status: 200 }));
    vi.stubGlobal("fetch", fetch);
    const cliente = new ClienteHttp();

    const resultado = await cliente.post("login", { correo: "ana@example.com" });

    expect(resultado).toEqual({
      tipo: "respuesta",
      estado: 200,
      cuerpo: { mensaje: "ok" },
    });
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:5001/login",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      }),
    );
  });
});

describe("RegistroHttpAdapter", () => {
  it("envía el usuario normalizado y traduce un registro exitoso", async () => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(respuesta(201, { mensaje: "Registro exitoso" }));
    const adapter = new RegistroHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    const resultado = await adapter.registrar(usuarioDePrueba());

    expect(resultado).toEqual({ estado: "exito", valor: undefined });
    expect(post).toHaveBeenCalledWith("registro", {
      nombre: "Ana",
      apellido: "Pérez",
      nickname: "anap",
      correo: "ana@example.com",
      contrasena: "Clave123",
    });
  });

  it("conserva el mensaje genérico de rechazo para no revelar duplicados", async () => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(
        respuesta(400, { error: "No se pudo completar el registro" }),
      );
    const adapter = new RegistroHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    const resultado = await adapter.registrar(usuarioDePrueba());

    expect(resultado).toEqual({
      estado: "error",
      error: {
        tipo: "validacion",
        mensaje: "No se pudo completar el registro",
      },
    });
  });

  it("traduce fallos de red a error de conexión", async () => {
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue({ tipo: "fallo", motivo: "conexion" });
    const adapter = new RegistroHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    const resultado = await adapter.registrar(usuarioDePrueba());

    expect(resultado).toEqual({
      estado: "error",
      error: { tipo: "conexion" },
    });
  });
});

describe("SessionHttpAdapter", () => {
  it("usa sesión incluida y programa el refresco tras el login", async () => {
    vi.useFakeTimers();
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(respuesta(200));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    const resultado = await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("clave anterior"),
    );

    expect(resultado).toEqual({ estado: "exito", valor: undefined });
    expect(post).toHaveBeenCalledWith("login", {
      correo: "ana@example.com",
      contrasena: "clave anterior",
    });
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);
    expect(post).toHaveBeenLastCalledWith("session/refresh");
    adapter.desmontar();
  });

  it("reintenta los fallos de conexión con backoff y conserva la sesión", async () => {
    vi.useFakeTimers();
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValueOnce(respuesta(200))
      .mockResolvedValueOnce({ tipo: "fallo", motivo: "conexion" })
      .mockResolvedValueOnce({ tipo: "fallo", motivo: "conexion" })
      .mockResolvedValueOnce(respuesta(200));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("secreto"),
    );
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);
    expect(post).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(1000);
    expect(post).toHaveBeenCalledTimes(3);
    await vi.advanceTimersByTimeAsync(2000);
    expect(post).toHaveBeenCalledTimes(4);
    adapter.desmontar();
  });

  it("reporta un refresh rechazado sin cerrar sesión automáticamente", async () => {
    vi.useFakeTimers();
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValueOnce(respuesta(200))
      .mockResolvedValueOnce(respuesta(401));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });
    const observar = vi.fn();
    adapter.observarEventos(observar);

    await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("secreto"),
    );
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);

    expect(observar).toHaveBeenCalledWith({ tipo: "refresco_rechazado" });
    expect(post).toHaveBeenCalledTimes(2);
    expect(post).not.toHaveBeenCalledWith("logout");
    adapter.desmontar();
  });

  it("limpia el temporizador al cerrar sesión", async () => {
    vi.useFakeTimers();
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValueOnce(respuesta(200))
      .mockResolvedValueOnce(respuesta(204));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });
    await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("secreto"),
    );

    const resultado = await adapter.cerrarSesion();
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);

    expect(resultado).toEqual({ estado: "exito", valor: undefined });
    expect(post).toHaveBeenCalledTimes(2);
    expect(post).toHaveBeenLastCalledWith("logout");
  });

  it("limpia el temporizador al desmontar el adaptador", async () => {
    vi.useFakeTimers();
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValue(respuesta(200));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });
    await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("secreto"),
    );

    adapter.desmontar();
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);

    expect(post).toHaveBeenCalledOnce();
  });

  it("espera un refresco en curso antes de expirar la cookie en logout", async () => {
    vi.useFakeTimers();
    let resolverRefresco!: (resultado: ResultadoHttp) => void;
    const respuestaRefresco = new Promise<ResultadoHttp>((resolve) => {
      resolverRefresco = resolve;
    });
    const post = vi
      .fn<ClienteHttpPort["post"]>()
      .mockResolvedValueOnce(respuesta(200))
      .mockReturnValueOnce(respuestaRefresco)
      .mockResolvedValueOnce(respuesta(204));
    const adapter = new SessionHttpAdapter({
      post,
      get: vi.fn<ClienteHttpPort["get"]>(),
    });

    await adapter.iniciarSesion(
      new CorreoElectronico("ana@example.com"),
      new ContraseñaDeInicioSesion("secreto"),
    );
    vi.advanceTimersByTime(15 * 60 * 1000);
    await Promise.resolve();

    const cierre = adapter.cerrarSesion();
    expect(post).toHaveBeenCalledTimes(2);
    resolverRefresco(respuesta(200));
    await cierre;

    expect(post).toHaveBeenCalledTimes(3);
    expect(post).toHaveBeenLastCalledWith("logout");
  });
});
