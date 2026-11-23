const URL_BASE_API =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";
const TIEMPO_LIMITE_MS = Number(
  import.meta.env.VITE_HTTP_TIMEOUT_MS || "10000",
);

if (!Number.isFinite(TIEMPO_LIMITE_MS) || TIEMPO_LIMITE_MS <= 0) {
  throw new Error("VITE_HTTP_TIMEOUT_MS debe ser un número positivo.");
}

export type ResultadoHttp =
  | { readonly tipo: "respuesta"; readonly estado: number; readonly cuerpo: unknown }
  | { readonly tipo: "fallo"; readonly motivo: "conexion" | "desconocido" };

export interface ClienteHttpPort {
  post(ruta: string, cuerpo?: unknown): Promise<ResultadoHttp>;
  get(ruta: string): Promise<ResultadoHttp>;
}

export class ClienteHttp implements ClienteHttpPort {
  async get(ruta: string): Promise<ResultadoHttp> {
    return this.request(ruta, { method: "GET" });
  }

  async post(ruta: string, cuerpo?: unknown): Promise<ResultadoHttp> {
    return this.request(ruta, {
      method: "POST",
      headers:
        cuerpo === undefined
          ? undefined
          : { "Content-Type": "application/json" },
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    });
  }

  private async request(
    ruta: string,
    opciones: RequestInit,
  ): Promise<ResultadoHttp> {
    const controlador = new AbortController();
    const temporizador = setTimeout(
      () => controlador.abort(),
      TIEMPO_LIMITE_MS,
    );

    try {
      const url = `${URL_BASE_API.replace(/\/+$/, "")}/${ruta.replace(/^\/+/, "")}`;
      const respuesta = await fetch(url, {
        ...opciones,
        credentials: "include",
        signal: controlador.signal,
      });

      const texto = await respuesta.text();
      let contenido: unknown;
      if (texto) {
        try {
          contenido = JSON.parse(texto);
        } catch {
          return { tipo: "fallo", motivo: "desconocido" };
        }
      }

      return {
        tipo: "respuesta",
        estado: respuesta.status,
        cuerpo: contenido,
      };
    } catch (error) {
      if (
        (error instanceof DOMException && error.name === "AbortError") ||
        error instanceof TypeError
      ) {
        return { tipo: "fallo", motivo: "conexion" };
      }
      return { tipo: "fallo", motivo: "desconocido" };
    } finally {
      clearTimeout(temporizador);
    }
  }
}
