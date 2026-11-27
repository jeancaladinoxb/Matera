#pragma once

#include <Arduino.h>

// Configuración persistente en la NVS del ESP32 (sobrevive a reinicios y a
// nuevas cargas de firmware, salvo que se borre la flash).
struct ConfigMatera {
  String ssid;
  String claveWifi;
  String urlBackend;   // p. ej. http://192.168.1.10:5001 o https://IP:5443/api
  String codigo;       // código de vinculación de 12 hex (secreto de fábrica)
  String token;        // JWT del dispositivo devuelto por /dispositivos/activar
  String certificadoCa;  // PEM de la CA para HTTPS (p. ej. rootCA.pem de mkcert)
  int sueloCrudoSeco;
  int sueloCrudoMojado;
  uint32_t intervaloS;
};

namespace almacenamiento {

void cargar(ConfigMatera& config);
void guardarWifi(const String& ssid, const String& clave);
void guardarSsid(const String& ssid);
void guardarClaveWifi(const String& clave);
void guardarUrlBackend(const String& url);
void guardarCodigo(const String& codigo);
void guardarToken(const String& token);
void borrarToken();
void guardarCertificadoCa(const String& pem);
void guardarCalibracion(int crudoSeco, int crudoMojado);
void guardarIntervalo(uint32_t segundos);
void borrarTodo();

}  // namespace almacenamiento
