#include "api_backend.h"

#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <math.h>

#include "config.h"
#include "logica.h"

namespace {

struct RespuestaHttp {
  bool redOk;
  int codigo;
  String cuerpo;
};

float redondear1(float valor) { return roundf(valor * 10.0f) / 10.0f; }

// POST JSON al backend. Usa HTTPS con validación de la CA guardada si la URL
// empieza por https://. Nunca desactiva la validación del certificado.
RespuestaHttp postJson(const ConfigMatera& config, const char* ruta, const String& cuerpo,
                       const String& token) {
  RespuestaHttp respuesta = {false, 0, ""};

  char url[256];
  if (!logica::unirUrl(config.urlBackend.c_str(), ruta, url, sizeof(url))) {
    Serial.println(F("[api] URL del backend demasiado larga o inválida."));
    return respuesta;
  }

  const bool esHttps = logica::empiezaCon(url, "https://");
  WiFiClient clientePlano;
  WiFiClientSecure clienteSeguro;
  WiFiClient* cliente = &clientePlano;

  if (esHttps) {
    if (config.certificadoCa.length() == 0) {
      Serial.println(F("[api] La URL es https:// pero no hay CA guardada. Usa el comando `setca`."));
      return respuesta;
    }
    clienteSeguro.setCACert(config.certificadoCa.c_str());
    cliente = &clienteSeguro;
  }

  HTTPClient http;
  http.setTimeout(TIMEOUT_HTTP_MS);
  http.setConnectTimeout(TIMEOUT_HTTP_MS);
  if (!http.begin(*cliente, url)) {
    Serial.println(F("[api] No se pudo preparar la petición HTTP."));
    return respuesta;
  }
  http.addHeader("Content-Type", "application/json");
  if (token.length() > 0) {
    http.addHeader("Authorization", "Bearer " + token);
  }

  int codigo = http.POST(cuerpo);
  if (codigo <= 0) {
    Serial.printf("[api] Error de conexión con %s: %s\n", url,
                  HTTPClient::errorToString(codigo).c_str());
    http.end();
    return respuesta;
  }

  respuesta.redOk = true;
  respuesta.codigo = codigo;
  respuesta.cuerpo = http.getString();
  http.end();
  return respuesta;
}

}  // namespace

namespace api_backend {

ResultadoActivacion activar(const ConfigMatera& config, const char* mac, String& tokenSalida) {
  JsonDocument peticion;
  peticion["mac"] = mac;
  peticion["codigo"] = config.codigo;
  String cuerpo;
  serializeJson(peticion, cuerpo);

  RespuestaHttp respuesta = postJson(config, "/dispositivos/activar", cuerpo, "");
  if (!respuesta.redOk) return ResultadoActivacion::ERROR_RED;

  switch (respuesta.codigo) {
    case 200: {
      JsonDocument datos;
      if (deserializeJson(datos, respuesta.cuerpo)) return ResultadoActivacion::ERROR_SERVIDOR;
      const char* token = datos["token"];
      if (token == nullptr || strlen(token) == 0) return ResultadoActivacion::ERROR_SERVIDOR;
      tokenSalida = token;
      return ResultadoActivacion::ACTIVADA;
    }
    case 409:
      return ResultadoActivacion::NO_VINCULADA;
    case 400:
    case 404:
      return ResultadoActivacion::CODIGO_INVALIDO;
    default:
      Serial.printf("[api] /dispositivos/activar respondió %d\n", respuesta.codigo);
      return ResultadoActivacion::ERROR_SERVIDOR;
  }
}

ResultadoEnvio enviarLectura(const ConfigMatera& config, const Lectura& lectura) {
  // Contrato propuesto para POST /lecturas. La MAC no viaja en el cuerpo:
  // el backend la obtiene del JWT del dispositivo (claim "sub").
  JsonDocument doc;
  if (lectura.sueloOk) doc["humedad_suelo"] = redondear1(lectura.humedadSuelo);
  else doc["humedad_suelo"] = nullptr;
  if (lectura.temperaturaOk) doc["temperatura"] = redondear1(lectura.temperatura);
  else doc["temperatura"] = nullptr;
  if (lectura.humedadAireOk) doc["humedad_aire"] = redondear1(lectura.humedadAire);
  else doc["humedad_aire"] = nullptr;
  if (lectura.luzOk) doc["luz_lux"] = redondear1(lectura.luzLux);
  else doc["luz_lux"] = nullptr;

  String cuerpo;
  serializeJson(doc, cuerpo);

  RespuestaHttp respuesta = postJson(config, "/lecturas", cuerpo, config.token);
  if (!respuesta.redOk) return ResultadoEnvio::ERROR_RED;

  if (respuesta.codigo == 200 || respuesta.codigo == 201) return ResultadoEnvio::ENVIADA;
  if (respuesta.codigo == 401 || respuesta.codigo == 403) return ResultadoEnvio::TOKEN_INVALIDO;
  if (respuesta.codigo == 404) return ResultadoEnvio::SIN_ENDPOINT;
  Serial.printf("[api] /lecturas respondió %d\n", respuesta.codigo);
  return ResultadoEnvio::ERROR_SERVIDOR;
}

const char* describir(ResultadoActivacion resultado) {
  switch (resultado) {
    case ResultadoActivacion::ACTIVADA: return "activada";
    case ResultadoActivacion::NO_VINCULADA: return "esperando a que vincules la matera en la web";
    case ResultadoActivacion::CODIGO_INVALIDO: return "MAC o código inválidos";
    case ResultadoActivacion::ERROR_RED: return "error de red";
    default: return "error del servidor";
  }
}

const char* describir(ResultadoEnvio resultado) {
  switch (resultado) {
    case ResultadoEnvio::ENVIADA: return "lectura enviada";
    case ResultadoEnvio::TOKEN_INVALIDO: return "token rechazado, se volverá a activar";
    case ResultadoEnvio::SIN_ENDPOINT: return "el backend aún no tiene POST /lecturas";
    case ResultadoEnvio::ERROR_RED: return "error de red";
    default: return "error del servidor";
  }
}

}  // namespace api_backend
