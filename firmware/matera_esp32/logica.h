#pragma once

// Lógica pura, sin dependencias de Arduino, para poder probarla en el PC
// (ver firmware/test/test_logica.cpp).

#include <ctype.h>
#include <stddef.h>
#include <string.h>

namespace logica {

// Convierte la lectura cruda del sensor capacitivo en porcentaje 0-100.
// En estos sensores el valor crudo BAJA cuando el suelo está más húmedo.
inline float porcentajeHumedadSuelo(int crudo, int crudoSeco, int crudoMojado) {
  if (crudoSeco == crudoMojado) {
    return -1.0f;  // calibración inválida
  }
  float porcentaje =
      100.0f * (float)(crudoSeco - crudo) / (float)(crudoSeco - crudoMojado);
  if (porcentaje < 0.0f) porcentaje = 0.0f;
  if (porcentaje > 100.0f) porcentaje = 100.0f;
  return porcentaje;
}

inline bool esHex(char c) { return isxdigit((unsigned char)c) != 0; }

// El backend acepta exactamente 12 caracteres hexadecimales.
inline bool codigoValido(const char* codigo) {
  if (codigo == nullptr || strlen(codigo) != 12) return false;
  for (size_t i = 0; i < 12; i++) {
    if (!esHex(codigo[i])) return false;
  }
  return true;
}

// Normaliza una MAC ("24:6f:28:ab:12:34", "24-6F-...") a 12 hex en mayúsculas,
// igual que el dominio Mac del backend. Devuelve false si no es válida.
inline bool normalizarMac(const char* entrada, char salida[13]) {
  if (entrada == nullptr) return false;
  size_t n = 0;
  for (const char* p = entrada; *p != '\0'; p++) {
    char c = *p;
    if (c == ':' || c == '-' || c == '.') continue;
    if (!esHex(c) || n >= 12) return false;
    salida[n++] = (char)toupper((unsigned char)c);
  }
  salida[n] = '\0';
  return n == 12;
}

// Interpreta el payload del QR de fábrica: "MAT:<MAC12>:<CODIGO12>".
inline bool parsearQr(const char* qr, char mac[13], char codigo[13]) {
  if (qr == nullptr || strncmp(qr, "MAT:", 4) != 0) return false;
  const char* resto = qr + 4;
  const char* separador = strrchr(resto, ':');
  if (separador == nullptr) return false;

  char macCruda[32];
  size_t largoMac = (size_t)(separador - resto);
  if (largoMac == 0 || largoMac >= sizeof(macCruda)) return false;
  memcpy(macCruda, resto, largoMac);
  macCruda[largoMac] = '\0';

  const char* cod = separador + 1;
  if (!normalizarMac(macCruda, mac) || !codigoValido(cod)) return false;
  strcpy(codigo, cod);
  return true;
}

// Une la URL base del backend con una ruta evitando dobles "/".
// "https://192.168.1.5:5443/api/" + "/lecturas" -> ".../api/lecturas"
inline bool unirUrl(const char* base, const char* ruta, char* salida, size_t tam) {
  if (base == nullptr || ruta == nullptr || tam == 0) return false;
  size_t largoBase = strlen(base);
  while (largoBase > 0 && base[largoBase - 1] == '/') largoBase--;
  while (*ruta == '/') ruta++;
  size_t necesario = largoBase + 1 + strlen(ruta) + 1;
  if (necesario > tam) return false;
  memcpy(salida, base, largoBase);
  salida[largoBase] = '/';
  strcpy(salida + largoBase + 1, ruta);
  return true;
}

inline bool empiezaCon(const char* texto, const char* prefijo) {
  return texto != nullptr && strncmp(texto, prefijo, strlen(prefijo)) == 0;
}

// Solo se aceptan http:// o https:// con algo después.
inline bool urlBackendValida(const char* url) {
  if (empiezaCon(url, "http://")) return strlen(url) > 7;
  if (empiezaCon(url, "https://")) return strlen(url) > 8;
  return false;
}

// Reconstruye un certificado PEM aunque se haya pegado en una sola línea o con
// saltos de línea extraños (el monitor serie de Arduino IDE suele unirlos):
// toma el base64 entre BEGIN y END, quita espacios y lo reenvuelve a 64 columnas.
inline bool normalizarPemCertificado(const char* entrada, char* salida, size_t tam) {
  static const char* const INICIO = "-----BEGIN CERTIFICATE-----";
  static const char* const FIN = "-----END CERTIFICATE-----";
  if (entrada == nullptr || salida == nullptr) return false;
  const char* ini = strstr(entrada, INICIO);
  if (ini == nullptr) return false;
  ini += strlen(INICIO);
  const char* fin = strstr(ini, FIN);
  if (fin == nullptr) return false;

  size_t n = 0;
  auto agregar = [&](char c) -> bool {
    if (n + 1 >= tam) return false;
    salida[n++] = c;
    return true;
  };
  for (const char* p = INICIO; *p; p++) if (!agregar(*p)) return false;
  if (!agregar('\n')) return false;

  size_t columna = 0;
  size_t base64 = 0;
  for (const char* p = ini; p < fin; p++) {
    char c = *p;
    if (c == ' ' || c == '\r' || c == '\n' || c == '\t') continue;
    bool permitido = isalnum((unsigned char)c) || c == '+' || c == '/' || c == '=';
    if (!permitido) return false;
    if (!agregar(c)) return false;
    base64++;
    if (++columna == 64) {
      if (!agregar('\n')) return false;
      columna = 0;
    }
  }
  if (base64 == 0) return false;
  if (columna != 0 && !agregar('\n')) return false;
  for (const char* p = FIN; *p; p++) if (!agregar(*p)) return false;
  if (!agregar('\n')) return false;
  salida[n] = '\0';
  return true;
}

}  // namespace logica
