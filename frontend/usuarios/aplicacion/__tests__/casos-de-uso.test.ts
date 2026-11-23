import { describe, expect, it, vi } from "vitest";

import { ErrorValidacionDominio } from "../../dominio/errores-dominio";
import { ContraseñaDeInicioSesion } from "../../dominio/contrasena-de-inicio-sesion";
import { CorreoElectronico } from "../../dominio/correo-electronico";
import { Usuario } from "../../dominio/usuario";
import { CerrarSesionUseCase } from "../casos-de-uso/cerrar-sesion-use-case";
import { IniciarSesionUseCase } from "../casos-de-uso/iniciar-sesion-use-case";
import { RegistrarUsuarioUseCase } from "../casos-de-uso/registrar-usuario-use-case";
import { fallo, exito } from "../resultado-aplicacion";
import { SessionPort } from "../puertos/salida/session-port";
import { UsuarioRepositoryPort } from "../puertos/salida/usuario-repository-port";

describe("RegistrarUsuarioUseCase", () => {
  it("crea los value objects y registra el usuario normalizado", async () => {
    const registrar = vi.fn<UsuarioRepositoryPort["registrar"]>().mockResolvedValue(
      exito(undefined),
    );
    const useCase = new RegistrarUsuarioUseCase({ registrar });

    const resultado = await useCase.registrarUsuario({
      nombre: "Ana",
      apellido: "Pérez",
      nickname: "anap",
      correo: " Ana@Example.COM ",
      contrasena: "Clave123",
    });

    expect(resultado).toEqual(exito(undefined));
    expect(registrar).toHaveBeenCalledOnce();
    const usuario = registrar.mock.calls[0][0];
    expect(usuario).toBeInstanceOf(Usuario);
    expect(usuario.correo.valor).toBe("ana@example.com");
    expect(usuario.contrasena.valor).toBe("Clave123");
  });

  it.each([
    {
      correo: "inválido",
      contrasena: "Clave123",
      nombre: "Ana",
      apellido: "Pérez",
      nickname: "anap",
    },
    {
      correo: "ana@example.com",
      contrasena: "clave123",
      nombre: "Ana",
      apellido: "Pérez",
      nickname: "anap",
    },
    {
      correo: "ana@example.com",
      contrasena: "Clave123",
      nombre: " ",
      apellido: "Pérez",
      nickname: "anap",
    },
  ])("rechaza datos inválidos antes de llamar al puerto", async (solicitud) => {
    const registrar = vi.fn<UsuarioRepositoryPort["registrar"]>();
    const useCase = new RegistrarUsuarioUseCase({ registrar });

    const resultado = await useCase.registrarUsuario(solicitud);

    expect(resultado.estado).toBe("error");
    if (resultado.estado === "error") {
      expect(resultado.error.tipo).toBe("validacion");
    }
    expect(registrar).not.toHaveBeenCalled();
  });

  it("devuelve el error de correo duplicado del puerto", async () => {
    const registrar = vi
      .fn<UsuarioRepositoryPort["registrar"]>()
      .mockResolvedValue(fallo({ tipo: "correo_duplicado" }));
    const useCase = new RegistrarUsuarioUseCase({ registrar });

    const resultado = await useCase.registrarUsuario({
      nombre: "Ana",
      apellido: "Pérez",
      nickname: "anap",
      correo: "ana@example.com",
      contrasena: "Clave123",
    });

    expect(resultado).toEqual(fallo({ tipo: "correo_duplicado" }));
  });
});

describe("IniciarSesionUseCase", () => {
  it("normaliza el correo y delega las credenciales válidas", async () => {
    const iniciarSesion = vi
      .fn<SessionPort["iniciarSesion"]>()
      .mockResolvedValue(exito(undefined));
    const cerrarSesion = vi
      .fn<SessionPort["cerrarSesion"]>()
      .mockResolvedValue(exito(undefined));
    const useCase = new IniciarSesionUseCase({ iniciarSesion, cerrarSesion });

    const resultado = await useCase.iniciarSesion({
      correo: " ANA@example.com ",
      contrasena: "clave anterior!",
    });

    expect(resultado).toEqual(exito(undefined));
    expect(iniciarSesion).toHaveBeenCalledOnce();
    expect(iniciarSesion.mock.calls[0][0]).toBeInstanceOf(CorreoElectronico);
    expect(iniciarSesion.mock.calls[0][0].valor).toBe("ana@example.com");
    expect(iniciarSesion.mock.calls[0][1]).toBeInstanceOf(
      ContraseñaDeInicioSesion,
    );
    expect(iniciarSesion.mock.calls[0][1].valor).toBe("clave anterior!");
  });

  it.each([
    { correo: "incorrecto", contrasena: "secreto" },
    { correo: "ana@example.com", contrasena: "" },
  ])("usa un error genérico y no llama al puerto para entradas inválidas", async (solicitud) => {
    const iniciarSesion = vi.fn<SessionPort["iniciarSesion"]>();
    const cerrarSesion = vi.fn<SessionPort["cerrarSesion"]>();
    const useCase = new IniciarSesionUseCase({ iniciarSesion, cerrarSesion });

    const resultado = await useCase.iniciarSesion(solicitud);

    expect(resultado).toEqual(fallo({ tipo: "credenciales_invalidas" }));
    expect(iniciarSesion).not.toHaveBeenCalled();
  });

  it("propaga errores tipados del puerto, incluidos los de conexión", async () => {
    const iniciarSesion = vi
      .fn<SessionPort["iniciarSesion"]>()
      .mockResolvedValue(fallo({ tipo: "conexion" }));
    const cerrarSesion = vi.fn<SessionPort["cerrarSesion"]>();
    const useCase = new IniciarSesionUseCase({ iniciarSesion, cerrarSesion });

    const resultado = await useCase.iniciarSesion({
      correo: "ana@example.com",
      contrasena: "secreto",
    });

    expect(resultado).toEqual(fallo({ tipo: "conexion" }));
  });
});

describe("CerrarSesionUseCase", () => {
  it("delega el cierre y devuelve el resultado tipado del puerto", async () => {
    const cerrarSesion = vi
      .fn<SessionPort["cerrarSesion"]>()
      .mockResolvedValue(exito(undefined));
    const iniciarSesion = vi.fn<SessionPort["iniciarSesion"]>();
    const useCase = new CerrarSesionUseCase({ iniciarSesion, cerrarSesion });

    const resultado = await useCase.cerrarSesion();

    expect(resultado).toEqual(exito(undefined));
    expect(cerrarSesion).toHaveBeenCalledOnce();
  });
});
