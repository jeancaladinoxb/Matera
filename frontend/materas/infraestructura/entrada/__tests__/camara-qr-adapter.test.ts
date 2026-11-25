import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const lectorMock = vi.hoisted(() => ({
  configuracion: [] as unknown[],
  start: vi.fn(),
  stop: vi.fn(),
  clear: vi.fn(),
  getCameras: vi.fn(),
}));

vi.mock("html5-qrcode", () => ({
  Html5Qrcode: class {
    constructor(_elementoId: string, configuracion: unknown) {
      lectorMock.configuracion.push(configuracion);
    }

    start(...argumentos: unknown[]) {
      return lectorMock.start(...argumentos);
    }

    stop() {
      return lectorMock.stop();
    }

    static getCameras() {
      return lectorMock.getCameras();
    }

    clear() {
      return lectorMock.clear();
    }
  },
  Html5QrcodeSupportedFormats: { QR_CODE: 0 },
}));

import { CamaraQrAdapter } from "../camara-qr-adapter";

describe("CamaraQrAdapter", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    lectorMock.configuracion.length = 0;
    lectorMock.start.mockResolvedValue(null);
    lectorMock.stop.mockResolvedValue(undefined);
    lectorMock.getCameras.mockResolvedValue([]);
    vi.stubGlobal("window", {
      isSecureContext: true,
      location: { hostname: "192.168.1.50" },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("inicia el lector limitado a QR usando toda la imagen de cámara", async () => {
    const getUserMedia = vi.fn();
    vi.stubGlobal("navigator", { mediaDevices: { getUserMedia } });
    const adapter = new CamaraQrAdapter();

    await expect(adapter.iniciar("lector-qr", vi.fn())).resolves.toBeUndefined();

    expect(lectorMock.configuracion).toEqual([
      { formatsToSupport: [0], verbose: false },
    ]);
    expect(lectorMock.start).toHaveBeenCalledWith(
      { facingMode: "environment" },
      expect.objectContaining({
        fps: 12,
        disableFlip: true,
        videoConstraints: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      }),
      expect.any(Function),
      expect.any(Function),
    );
    expect(getUserMedia).not.toHaveBeenCalled();

    expect(lectorMock.start.mock.calls[0][1]).not.toHaveProperty("qrbox");

    await adapter.detener();
    expect(lectorMock.stop).toHaveBeenCalledOnce();
    expect(lectorMock.clear).toHaveBeenCalledOnce();
  });

  it("reintenta la cámara trasera sin resolución fija si falla la preferida", async () => {
    const getUserMedia = vi.fn();
    vi.stubGlobal("navigator", { mediaDevices: { getUserMedia } });
    lectorMock.start
      .mockRejectedValueOnce(new Error("OverconstrainedError"))
      .mockResolvedValueOnce(null);
    const adapter = new CamaraQrAdapter();

    await expect(adapter.iniciar("lector-qr", vi.fn())).resolves.toBeUndefined();

    expect(lectorMock.start).toHaveBeenCalledTimes(2);
    expect(lectorMock.start.mock.calls[1][1]).toEqual(
      expect.objectContaining({
        videoConstraints: { facingMode: { ideal: "environment" } },
      }),
    );
    expect(lectorMock.start.mock.calls[1][1]).not.toHaveProperty("qrbox");
    expect(lectorMock.getCameras).not.toHaveBeenCalled();
  });

  it("prueba las cámaras disponibles si no inicia la cámara trasera", async () => {
    vi.stubGlobal("navigator", {
      mediaDevices: { getUserMedia: vi.fn() },
    });
    lectorMock.start
      .mockRejectedValueOnce(new Error("OverconstrainedError"))
      .mockRejectedValueOnce(new Error("OverconstrainedError"))
      .mockResolvedValueOnce(null);
    lectorMock.getCameras.mockResolvedValue([
      { id: "frontal", label: "Front Camera" },
      { id: "trasera", label: "Back Camera" },
    ]);
    const adapter = new CamaraQrAdapter();

    const resultado = await adapter.iniciar("lector-qr", vi.fn());

    expect(lectorMock.getCameras).toHaveBeenCalledOnce();
    expect(resultado).toBeUndefined();
    expect(lectorMock.start).toHaveBeenCalledTimes(3);
    expect(lectorMock.start.mock.calls[2][0]).toBe("trasera");
  });
});
