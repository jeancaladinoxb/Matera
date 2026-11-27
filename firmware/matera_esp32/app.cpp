#include <WiFi.h>
#include <esp_mac.h>

#include "almacenamiento.h"
#include "api_backend.h"
#include "config.h"
#include "consola.h"
#include "sensores.h"
#include "app.h"

namespace {

ConfigMatera config;
char mac[13];

unsigned long proximoIntentoWifi = 0;
unsigned long proximaActivacion = 0;
unsigned long proximaLectura = 0;
bool wifiConectadoAntes = false;
bool codigoRechazado = false;

// Compara tiempos sin fallar cuando millis() da la vuelta (~49 días).
bool llego(unsigned long objetivo) { return (long)(millis() - objetivo) >= 0; }

void leerMac() {
  uint8_t bytes[6];
  esp_read_mac(bytes, ESP_MAC_WIFI_STA);
  snprintf(mac, sizeof(mac), "%02X%02X%02X%02X%02X%02X", bytes[0], bytes[1], bytes[2],
           bytes[3], bytes[4], bytes[5]);
}

bool listaParaActivar() {
  return config.urlBackend.length() > 0 && config.codigo.length() > 0;
}

void mostrarPendientes() {
  if (config.ssid.length() == 0) Serial.println(F("Falta WiFi: setssid <nombre> y setclave <clave>"));
  if (config.urlBackend.length() == 0) Serial.println(F("Falta backend: setbackend <url>"));
  if (config.codigo.length() == 0) Serial.println(F("Falta código: setcodigo <12 hex> o setqr MAT:..."));
}

void imprimirLectura(const Lectura& l) {
  Serial.print(F("[lectura] suelo="));
  if (l.sueloOk) Serial.printf("%.1f%% (crudo %d)", l.humedadSuelo, l.sueloCrudo);
  else Serial.printf("error (crudo %d)", l.sueloCrudo);
  Serial.print(F("  temp="));
  if (l.temperaturaOk) Serial.printf("%.1f C", l.temperatura);
  else Serial.print(F("error"));
  Serial.print(F("  aire="));
  if (l.humedadAireOk) Serial.printf("%.1f%%", l.humedadAire);
  else Serial.print(F("error"));
  Serial.print(F("  luz="));
  if (l.luzOk) Serial.printf("%.1f lx\n", l.luzLux);
  else Serial.println(F("error"));
}

void gestionarWifi() {
  const bool conectado = WiFi.status() == WL_CONNECTED;
  if (conectado != wifiConectadoAntes) {
    wifiConectadoAntes = conectado;
    if (conectado) {
      Serial.printf("[wifi] Conectado a %s, IP %s\n", config.ssid.c_str(),
                    WiFi.localIP().toString().c_str());
      proximaActivacion = millis();
    } else {
      Serial.println(F("[wifi] Desconectado."));
    }
  }
  if (conectado || config.ssid.length() == 0 || !llego(proximoIntentoWifi)) return;

  Serial.printf("[wifi] Conectando a %s...\n", config.ssid.c_str());
  WiFi.begin(config.ssid.c_str(), config.claveWifi.c_str());
  proximoIntentoWifi = millis() + REINTENTO_WIFI_S * 1000UL;
}

void gestionarActivacion() {
  if (WiFi.status() != WL_CONNECTED || config.token.length() > 0 || codigoRechazado ||
      !listaParaActivar() || !llego(proximaActivacion)) {
    return;
  }

  String token;
  ResultadoActivacion resultado = api_backend::activar(config, mac, token);
  Serial.printf("[activar] %s\n", api_backend::describir(resultado));

  switch (resultado) {
    case ResultadoActivacion::ACTIVADA:
      config.token = token;
      almacenamiento::guardarToken(token);
      proximaLectura = millis();  // primera lectura de inmediato
      break;
    case ResultadoActivacion::NO_VINCULADA:
      Serial.printf("[activar] En la web vincula la matera con la MAC %s y tu código.\n", mac);
      proximaActivacion = millis() + REINTENTO_ACTIVACION_S * 1000UL;
      break;
    case ResultadoActivacion::CODIGO_INVALIDO:
      Serial.println(F("[activar] Revisa el código (setcodigo) o registra la MAC con el CLI del backend."));
      codigoRechazado = true;  // no se reintenta hasta cambiar la configuración
      break;
    default:
      proximaActivacion = millis() + REINTENTO_ACTIVACION_S * 1000UL;
      break;
  }
}

void gestionarLecturas() {
  if (!llego(proximaLectura)) return;
  proximaLectura = millis() + config.intervaloS * 1000UL;

  Lectura lectura = sensores::leer(config.sueloCrudoSeco, config.sueloCrudoMojado);
  imprimirLectura(lectura);

  if (WiFi.status() != WL_CONNECTED || config.token.length() == 0) return;

  ResultadoEnvio resultado = api_backend::enviarLectura(config, lectura);
  Serial.printf("[envio] %s\n", api_backend::describir(resultado));
  if (resultado == ResultadoEnvio::TOKEN_INVALIDO) {
    config.token = "";
    almacenamiento::borrarToken();
    proximaActivacion = millis();
  }
}

}  // namespace

namespace app {

void iniciar() {
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\n=== Matera Inteligente - ESP32 ==="));

  almacenamiento::cargar(config);
  leerMac();
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  sensores::iniciar();

  consola::mostrarEstado(config, mac);
  mostrarPendientes();
  Serial.println(F("Escribe `ayuda` para ver los comandos."));

  // La primera lectura espera 2 s para que el DHT22 se estabilice.
  proximaLectura = millis() + 2000UL;
}

void ciclo() {
  EventosConsola eventos = consola::procesar(config, mac);
  if (eventos.reconectarWifi) {
    WiFi.disconnect();
    proximoIntentoWifi = millis();
  }
  if (eventos.reiniciarActivacion) {
    codigoRechazado = false;
    proximaActivacion = millis();
  }
  if (eventos.leerAhora) {
    proximaLectura = millis();
  }

  gestionarWifi();
  gestionarActivacion();
  gestionarLecturas();
  delay(10);
}

}  // namespace app
