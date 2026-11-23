import { Html5Qrcode } from "html5-qrcode";

export type ErrorCamaraQr =
  | "permiso_denegado"
  | "sin_camara"
  | "contexto_inseguro"
  | "error_desconocido";

export class CamaraQrAdapter {
  private lector: Html5Qrcode | undefined;
  private iniciado = false;

  async iniciar(
    elementoId: string,
    alLeer: (texto: string) => void,
  ): Promise<ErrorCamaraQr | undefined> {
    if (
      typeof window === "undefined" ||
      (!window.isSecureContext &&
        !["localhost", "127.0.0.1"].includes(window.location.hostname))
    ) {
      return "contexto_inseguro";
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      return "sin_camara";
    }

    try {
      const permiso = await navigator.mediaDevices.getUserMedia({ video: true });
      permiso.getTracks().forEach((pista) => pista.stop());
      const camaras = await Html5Qrcode.getCameras();
      if (camaras.length === 0) {
        return "sin_camara";
      }

      this.lector = new Html5Qrcode(elementoId);
      await this.lector.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 220, height: 220 },
          aspectRatio: 1,
        },
        (texto) => {
          alLeer(texto);
        },
        () => undefined,
      );
      this.iniciado = true;
      return undefined;
    } catch (error) {
      const nombre =
        error instanceof DOMException ? error.name : "";
      if (
        nombre === "NotAllowedError" ||
        nombre === "PermissionDeniedError"
      ) {
        return "permiso_denegado";
      }
      if (
        nombre === "NotFoundError" ||
        nombre === "DevicesNotFoundError"
      ) {
        return "sin_camara";
      }
      return "error_desconocido";
    }
  }

  async detener(): Promise<void> {
    if (!this.lector) {
      return;
    }
    try {
      if (this.iniciado) {
        await this.lector.stop();
      }
      this.lector.clear();
    } finally {
      this.iniciado = false;
      this.lector = undefined;
    }
  }
}
