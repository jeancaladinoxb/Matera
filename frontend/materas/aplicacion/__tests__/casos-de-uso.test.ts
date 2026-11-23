import { describe, expect, it, vi } from "vitest";

import { exito, fallo } from "../../../usuarios/aplicacion/resultado-aplicacion";
import { VincularMateraUseCase } from "../casos-de-uso/vincular-matera-use-case";
import { VincularMateraDesdeQrUseCase } from "../casos-de-uso/vincular-matera-desde-qr-use-case";
import { ConsultarMateraDelUsuarioUseCase } from "../casos-de-uso/consultar-matera-del-usuario-use-case";
import { MateraRepositoryPort } from "../puertos/salida/matera-repository-port";

function crearRepository() {
  return {
    vincular: vi.fn<MateraRepositoryPort["vincular"]>(),
    consultarMateraDelUsuario:
      vi.fn<MateraRepositoryPort["consultarMateraDelUsuario"]>(),
  } satisfies MateraRepositoryPort;
}

describe("VincularMateraUseCase", () => {
  it("normaliza MAC y delega el código sin llamar a otros servicios", async () => {
    const repository = crearRepository();
    repository.vincular.mockResolvedValue(exito(undefined));
    const useCase = new VincularMateraUseCase(repository);

    const resultado = await useCase.vincular({
      mac: "24:6f:28:ab:12:34",
      codigo: "9F3A1C7E0B52",
    });

    expect(resultado).toEqual(exito(undefined));
    expect(repository.vincular).toHaveBeenCalledWith(
      "246F28AB1234",
      "9f3a1c7e0b52",
    );
  });

  it.each([
    { mac: "", codigo: "9f3a1c7e0b52" },
    { mac: "246F28AB1234", codigo: "" },
    { mac: "246F28AB12G4", codigo: "9f3a1c7e0b52" },
  ])("rechaza datos inválidos antes de tocar el puerto", async (solicitud) => {
    const repository = crearRepository();
    const useCase = new VincularMateraUseCase(repository);

    const resultado = await useCase.vincular(solicitud);

    expect(resultado.estado).toBe("error");
    expect(repository.vincular).not.toHaveBeenCalled();
  });

  it("propaga los errores tipados del puerto", async () => {
    const repository = crearRepository();
    repository.vincular.mockResolvedValue(
      fallo({ tipo: "matera_codigo_invalido" }),
    );
    const useCase = new VincularMateraUseCase(repository);

    const resultado = await useCase.vincular({
      mac: "246F28AB1234",
      codigo: "9f3a1c7e0b52",
    });

    expect(resultado).toEqual(
      fallo({ tipo: "matera_codigo_invalido" }),
    );
  });

  it("convierte una excepción inesperada del puerto en desconocido", async () => {
    const repository = crearRepository();
    repository.vincular.mockRejectedValue(new Error("fallo secreto"));
    const useCase = new VincularMateraUseCase(repository);

    const resultado = await useCase.vincular({
      mac: "246F28AB1234",
      codigo: "9f3a1c7e0b52",
    });

    expect(resultado).toEqual(fallo({ tipo: "desconocido" }));
  });
});

describe("VincularMateraDesdeQrUseCase", () => {
  it("interpreta el QR y delega en el caso de vinculación", async () => {
    const vincular = vi.fn().mockResolvedValue(exito(undefined));
    const useCase = new VincularMateraDesdeQrUseCase({ vincular });

    const resultado = await useCase.vincularDesdeQr(
      "MAT:24:6f:28:ab:12:34:9F3A1C7E0B52",
    );

    expect(resultado).toEqual(exito(undefined));
    expect(vincular).toHaveBeenCalledWith({
      mac: "246F28AB1234",
      codigo: "9f3a1c7e0b52",
    });
  });

  it("rechaza un QR inválido sin delegar", async () => {
    const vincular = vi.fn();
    const useCase = new VincularMateraDesdeQrUseCase({ vincular });

    const resultado = await useCase.vincularDesdeQr("QR inválido");

    expect(resultado.estado).toBe("error");
    expect(vincular).not.toHaveBeenCalled();
  });
});

describe("ConsultarMateraDelUsuarioUseCase", () => {
  it("devuelve directamente el resultado del puerto", async () => {
    const repository = crearRepository();
    repository.consultarMateraDelUsuario.mockResolvedValue(
      exito({ vinculada: true, mac: "246F28AB1234" }),
    );
    const useCase = new ConsultarMateraDelUsuarioUseCase(repository);

    const resultado = await useCase.consultarMateraDelUsuario();

    expect(resultado).toEqual(
      exito({ vinculada: true, mac: "246F28AB1234" }),
    );
  });
});
