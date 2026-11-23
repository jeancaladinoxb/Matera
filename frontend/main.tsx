import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./usuarios/infraestructura/entrada/estilos.css";
import { App } from "./usuarios/infraestructura/entrada/app";
import { crearComposicionUsuarios } from "./usuarios/infraestructura/composicion/composicion-root";

const raiz = document.getElementById("root");
if (!raiz) {
  throw new Error("No se encontró el elemento raíz de la aplicación.");
}

const composicion = crearComposicionUsuarios();
createRoot(raiz).render(
  <StrictMode>
    <App composicion={composicion} />
  </StrictMode>,
);
