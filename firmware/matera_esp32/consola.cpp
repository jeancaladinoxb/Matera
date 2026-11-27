#include "consola.h"

#include <WiFi.h>

#include "config.h"
#include "logica.h"
#include "sensores.h"

namespace {

String linea;
bool modoCertificado = false;
String bufferCertificado;
const size_t MAX_LINEA = 512;
const size_t MAX_CERTIFICADO = 4000;  // límite de un texto en la NVS

String argumento(const String& comando, const char* nombre) {
  String resto = comando.substring(strlen(nombre));
  resto.trim();
  return resto;
}

String enmascarar(const String& valor, size_t visibles) {
  if (valor.length() == 0) return String("(vacío)");
  if (valor.length() <= visibles) return String("****");
  String resultado = valor.substring(0, visibles);
  resultado += "... (";
  resultado += String((unsigned)valor.length());
  resultado += " caracteres)";
  return resultado;
}

void terminarCertificado(ConfigMatera& config, EventosConsola& eventos) {
  modoCertificado = false;
  static char pem[MAX_CERTIFICADO + 64];
  if (!logica::normalizarPemCertificado(bufferCertificado.c_str(), pem, sizeof(pem))) {
    Serial.println(F("Certificado inválido. Debe incluir BEGIN CERTIFICATE y END CERTIFICATE."));
    bufferCertificado = "";
    return;
  }
  bufferCertificado = "";
  config.certificadoCa = pem;
  almacenamiento::guardarCertificadoCa(config.certificadoCa);
  Serial.println(F("CA guardada. Se usará para validar el servidor HTTPS."));
  eventos.reiniciarActivacion = true;
}

void ejecutar(const String& comando, ConfigMatera& config, const char* mac,
              EventosConsola& eventos) {
  if (comando.length() == 0) return;

  if (comando == "ayuda" || comando == "help") {
    consola::mostrarAyuda();
  } else if (comando == "estado") {
    consola::mostrarEstado(config, mac);
  } else if (comando.startsWith("setssid ")) {
    config.ssid = argumento(comando, "setssid");
    almacenamiento::guardarSsid(config.ssid);
    Serial.println("SSID guardado: " + config.ssid);
    eventos.reconectarWifi = true;
  } else if (comando.startsWith("setclave")) {
    config.claveWifi = argumento(comando, "setclave");
    almacenamiento::guardarClaveWifi(config.claveWifi);
    Serial.println(F("Clave WiFi guardada."));
    eventos.reconectarWifi = true;
  } else if (comando.startsWith("setbackend ")) {
    String url = argumento(comando, "setbackend");
    if (!logica::urlBackendValida(url.c_str())) {
      Serial.println(F("URL inválida. Ejemplos: http://192.168.1.10:5001  o  https://192.168.78.154:5443/api"));
      return;
    }
    config.urlBackend = url;
    almacenamiento::guardarUrlBackend(url);
    Serial.println("Backend guardado: " + url);
    if (url.startsWith("https://") && config.certificadoCa.length() == 0) {
      Serial.println(F("Ojo: para https falta la CA. Usa `setca` y pega el rootCA.pem."));
    }
    eventos.reiniciarActivacion = true;
  } else if (comando.startsWith("setcodigo ")) {
    String codigo = argumento(comando, "setcodigo");
    if (!logica::codigoValido(codigo.c_str())) {
      Serial.println(F("El código debe tener exactamente 12 caracteres hexadecimales."));
      return;
    }
    codigo.toLowerCase();
    config.codigo = codigo;
    almacenamiento::guardarCodigo(codigo);
    Serial.println(F("Código guardado."));
    eventos.reiniciarActivacion = true;
  } else if (comando.startsWith("setqr ")) {
    String qr = argumento(comando, "setqr");
    char macQr[13];
    char codigo[13];
    if (!logica::parsearQr(qr.c_str(), macQr, codigo)) {
      Serial.println(F("QR inválido. Formato: MAT:<MAC>:<CODIGO>"));
      return;
    }
    if (strcmp(macQr, mac) != 0) {
      Serial.printf("Ese QR es de la MAC %s, pero este ESP32 es %s.\n", macQr, mac);
      return;
    }
    String codigoTexto = codigo;
    codigoTexto.toLowerCase();
    config.codigo = codigoTexto;
    almacenamiento::guardarCodigo(config.codigo);
    Serial.println(F("Código del QR guardado."));
    eventos.reiniciarActivacion = true;
  } else if (comando == "setca") {
    modoCertificado = true;
    bufferCertificado = "";
    Serial.println(F("Pega el certificado PEM completo (hasta -----END CERTIFICATE-----)."));
  } else if (comando == "borrarca") {
    config.certificadoCa = "";
    almacenamiento::guardarCertificadoCa("");
    Serial.println(F("CA borrada."));
  } else if (comando.startsWith("intervalo ")) {
    long segundos = argumento(comando, "intervalo").toInt();
    if (segundos < INTERVALO_MINIMO_S) {
      Serial.printf("El intervalo mínimo es %d s.\n", INTERVALO_MINIMO_S);
      return;
    }
    config.intervaloS = (uint32_t)segundos;
    almacenamiento::guardarIntervalo(config.intervaloS);
    Serial.printf("Se enviará una lectura cada %lu s.\n", (unsigned long)config.intervaloS);
  } else if (comando == "calibrar seco") {
    config.sueloCrudoSeco = sensores::leerSueloCrudo();
    almacenamiento::guardarCalibracion(config.sueloCrudoSeco, config.sueloCrudoMojado);
    Serial.printf("Seco = %d (sensor al aire, limpio y seco).\n", config.sueloCrudoSeco);
  } else if (comando == "calibrar mojado") {
    config.sueloCrudoMojado = sensores::leerSueloCrudo();
    almacenamiento::guardarCalibracion(config.sueloCrudoSeco, config.sueloCrudoMojado);
    Serial.printf("Mojado = %d (sensor en agua hasta la línea).\n", config.sueloCrudoMojado);
  } else if (comando == "leer") {
    eventos.leerAhora = true;
  } else if (comando == "reactivar") {
    config.token = "";
    almacenamiento::borrarToken();
    Serial.println(F("Token borrado. Se volverá a activar."));
    eventos.reiniciarActivacion = true;
  } else if (comando == "borrar") {
    almacenamiento::borrarTodo();
    Serial.println(F("Configuración borrada. Reiniciando..."));
    delay(500);
    ESP.restart();
  } else if (comando == "reiniciar") {
    ESP.restart();
  } else {
    Serial.println("Comando desconocido: " + comando + ". Escribe `ayuda`.");
  }
}

}  // namespace

namespace consola {

void mostrarAyuda() {
  Serial.println(F(
      "\nComandos:\n"
      "  estado                  muestra la configuración y el estado\n"
      "  setssid <nombre>        nombre de la red WiFi (admite espacios)\n"
      "  setclave <clave>        clave de la red WiFi (vacía si es abierta)\n"
      "  setbackend <url>        http://IP:5001  o  https://IP:5443/api\n"
      "  setcodigo <12 hex>      código de vinculación de esta matera\n"
      "  setqr MAT:<MAC>:<COD>   igual que setcodigo, pegando el QR de fábrica\n"
      "  setca                   pegar la CA (rootCA.pem) para usar https\n"
      "  borrarca                quita la CA guardada\n"
      "  intervalo <segundos>    cada cuánto enviar lecturas\n"
      "  calibrar seco           sensor de suelo al aire\n"
      "  calibrar mojado         sensor de suelo en un vaso de agua\n"
      "  leer                    lee y envía una lectura ahora\n"
      "  reactivar               borra el token y vuelve a activar\n"
      "  reiniciar | borrar      reinicia | borra toda la configuración\n"));
}

void mostrarEstado(const ConfigMatera& config, const char* mac) {
  Serial.println(F("\n--- Matera ESP32 ---"));
  Serial.printf("Firmware:        %s\n", VERSION_FIRMWARE);
  Serial.printf("MAC:             %s\n", mac);
  const bool conectado = WiFi.status() == WL_CONNECTED;
  Serial.printf("WiFi:            %s (%s)\n",
                config.ssid.length() ? config.ssid.c_str() : "(sin configurar)",
                conectado ? "conectado" : "desconectado");
  if (conectado) {
    Serial.printf("IP:              %s\n", WiFi.localIP().toString().c_str());
  }
  Serial.printf("Backend:         %s\n",
                config.urlBackend.length() ? config.urlBackend.c_str() : "(sin configurar)");
  Serial.printf("CA HTTPS:        %s\n", config.certificadoCa.length() ? "guardada" : "no");
  Serial.printf("Código:          %s\n", enmascarar(config.codigo, 2).c_str());
  Serial.printf("Token:           %s\n", config.token.length() ? "activada" : "sin activar");
  Serial.printf("Suelo seco/mojado: %d / %d\n", config.sueloCrudoSeco, config.sueloCrudoMojado);
  Serial.printf("Medidor de luz:  %s\n", sensores::hayMedidorDeLuz() ? "BH1750 detectado" : "no detectado");
  Serial.printf("Intervalo:       %lu s\n", (unsigned long)config.intervaloS);
}

EventosConsola procesar(ConfigMatera& config, const char* mac) {
  EventosConsola eventos;
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (modoCertificado) {
      if (bufferCertificado.length() < MAX_CERTIFICADO) bufferCertificado += c;
      if (bufferCertificado.indexOf("-----END CERTIFICATE-----") >= 0) {
        terminarCertificado(config, eventos);
      } else if (bufferCertificado.length() >= MAX_CERTIFICADO) {
        Serial.println(F("Certificado demasiado largo."));
        modoCertificado = false;
        bufferCertificado = "";
      }
      continue;
    }

    if (c == '\r' || c == '\n') {
      String comando = linea;
      linea = "";
      comando.trim();
      ejecutar(comando, config, mac, eventos);
    } else if (linea.length() < MAX_LINEA) {
      linea += c;
    }
  }
  return eventos;
}

}  // namespace consola
