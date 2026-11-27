#pragma once

#include <Arduino.h>

#include "almacenamiento.h"
#include "sensores.h"

enum class ResultadoActivacion {
  ACTIVADA,          // 200: llegó el token
  NO_VINCULADA,      // 409: el usuario aún no ha vinculado la matera en la web
  CODIGO_INVALIDO,   // 404: MAC o código incorrectos (no sirve reintentar)
  ERROR_RED,         // sin conexión, timeout o TLS
  ERROR_SERVIDOR,    // cualquier otra respuesta
};

enum class ResultadoEnvio {
  ENVIADA,           // 200/201
  TOKEN_INVALIDO,    // 401/403: hay que volver a activar
  SIN_ENDPOINT,      // 404: el backend aún no tiene POST /lecturas
  ERROR_RED,
  ERROR_SERVIDOR,
};

namespace api_backend {

// mac: 12 hex en mayúsculas. Si devuelve ACTIVADA, `tokenSalida` trae el JWT.
ResultadoActivacion activar(const ConfigMatera& config, const char* mac, String& tokenSalida);

ResultadoEnvio enviarLectura(const ConfigMatera& config, const Lectura& lectura);

const char* describir(ResultadoActivacion resultado);
const char* describir(ResultadoEnvio resultado);

}  // namespace api_backend
