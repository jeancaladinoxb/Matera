import {
  Html5Qrcode,
  Html5QrcodeSupportedFormats,
} from "html5-qrcode";

export type ErrorCamaraQr =
  | "permiso_denegado"
  | "sin_camara"
  | "contexto_inseguro"
  | "error_desconocido";

export class CamaraQrAdapter {
  private lector: Html5Qrcode | undefined;
  private iniciado = false;
  private operacion: Promise<void> = Promise.resolve();

  private enOrden<T>(accion: () => Promise<T>): Promise<T> {
    const resultado = this.operacion.then(accion);
    this.operacion = resultado.then(() => undefined, () => undefined);
    return resultado;
  }

  iniciar(
    elementoId: string,
    alLeer: (texto: string) => void,
  ): Promise<ErrorCamaraQr | undefined> {
    return this.enOrden(() => this.abrir(elementoId, alLeer));
  }

  private async abrir(
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
      this.lector = new Html5Qrcode(elementoId, {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
        verbose: false,
      });
    } catch (error) {
      return this.clasificarError(error);
    }

    const opcionesEscaneo = {
      fps: 12,
      disableFlip: true,
    };
    const camaraTrasera = { facingMode: "environment" };
    let ultimoError: unknown;

    for (const videoConstraints of [
      {
        facingMode: { ideal: "environment" },
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      { facingMode: { ideal: "environment" } },
    ]) {
      try {
        await this.lector.start(
          camaraTrasera,
          { ...opcionesEscaneo, videoConstraints },
          alLeer,
          () => undefined,
        );
        this.iniciado = true;
        return undefined;
      } catch (error) {
        ultimoError = error;
        if (this.clasificarError(error) === "permiso_denegado") {
          return "permiso_denegado";
        }
      }
    }

    let camaras;
    try {
      camaras = await Html5Qrcode.getCameras();
    } catch (error) {
      return this.clasificarError(error);
    }
    if (camaras.length === 0) {
      return "sin_camara";
    }

    const camarasOrdenadas = [...camaras].sort((a, b) => {
      const trasera = /back|rear|environment|trasera|posterior/i;
      return Number(trasera.test(b.label)) - Number(trasera.test(a.label));
    });
    for (const camara of camarasOrdenadas) {
      try {
        await this.lector.start(
          camara.id,
          opcionesEscaneo,
          alLeer,
          () => undefined,
        );
        this.iniciado = true;
        return undefined;
      } catch (error) {
        ultimoError = error;
        if (this.clasificarError(error) === "permiso_denegado") {
          return "permiso_denegado";
        }
      }
    }
    return this.clasificarError(ultimoError);
  }

  private clasificarError(error: unknown): ErrorCamaraQr {
    const detalle =
      error instanceof Error
        ? `${error.name} ${error.message}`
        : String(error);
    if (/NotAllowedError|PermissionDeniedError/i.test(detalle)) {
      return "permiso_denegado";
    }
    if (/NotFoundError|DevicesNotFoundError/i.test(detalle)) {
      return "sin_camara";
    }
    return "error_desconocido";
  }

  async leerFoto(elementoId: string, foto: File): Promise<string> {
    const lector = new Html5Qrcode(elementoId);
    try {
      const reducida = await this.reducirFoto(foto).catch(() => foto);
      if (reducida !== foto) {
        try {
          return await lector.scanFile(reducida, false);
        } catch {
          // Un QR lejano puede necesitar la resolución original.
        }
      }
      return await lector.scanFile(foto, false);
    } finally {
      lector.clear();
    }
  }

  private async reducirFoto(foto: File): Promise<File> {
    const url = URL.createObjectURL(foto);
    try {
      const imagen = new Image();
      imagen.src = url;
      await imagen.decode();

      // Reducir la trama visible de los píxeles de la OLED antes de decodificar.
      const escala = 1008 / Math.max(imagen.naturalWidth, imagen.naturalHeight);
      if (escala >= 1) return foto;

      const origen = document.createElement("canvas");
      origen.width = imagen.naturalWidth;
      origen.height = imagen.naturalHeight;
      const captura = origen.getContext("2d", { willReadFrequently: true });
      if (!captura) return foto;
      captura.drawImage(imagen, 0, 0);
      const pixeles = captura.getImageData(0, 0, origen.width, origen.height).data;

      const bloque = Math.max(2, Math.round(1 / escala));
      const lienzo = document.createElement("canvas");
      lienzo.width = Math.max(1, Math.floor(origen.width / bloque));
      lienzo.height = Math.max(1, Math.floor(origen.height / bloque));
      const contexto = lienzo.getContext("2d");
      if (!contexto) return foto;
      const salida = contexto.createImageData(lienzo.width, lienzo.height);

      // El canal verde conserva el contraste de esta OLED azul.
      for (let y = 0; y < lienzo.height; y++) {
        for (let x = 0; x < lienzo.width; x++) {
          let suma = 0;
          for (let fila = 0; fila < bloque; fila++) {
            const inicio = ((y * bloque + fila) * origen.width + x * bloque) * 4 + 1;
            for (let columna = 0; columna < bloque; columna++) {
              suma += pixeles[inicio + columna * 4];
            }
          }
          const gris = suma / (bloque * bloque);
          const indice = (y * lienzo.width + x) * 4;
          salida.data[indice] = gris;
          salida.data[indice + 1] = gris;
          salida.data[indice + 2] = gris;
          salida.data[indice + 3] = 255;
        }
      }
      contexto.putImageData(salida, 0, 0);
      origen.width = 0;
      origen.height = 0;

      const datos = await new Promise<Blob | null>((resolver) => lienzo.toBlob(resolver));
      return datos ? new File([datos], "qr.png", { type: datos.type }) : foto;
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  detener(): Promise<void> {
    return this.enOrden(() => this.cerrar());
  }

  private async cerrar(): Promise<void> {
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
