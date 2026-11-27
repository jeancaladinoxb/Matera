// Pruebas de la lógica pura del firmware, ejecutables en el PC:
//   cd firmware/pruebas_pc
//   g++ -std=c++17 -Wall -Wextra -I../matera_esp32 test_logica.cpp -o test_logica && ./test_logica
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>

#include "logica.h"

using namespace logica;

static void prueba_porcentaje_suelo() {
  assert(porcentajeHumedadSuelo(2900, 2900, 1300) == 0.0f);
  assert(porcentajeHumedadSuelo(1300, 2900, 1300) == 100.0f);
  assert(std::fabs(porcentajeHumedadSuelo(2100, 2900, 1300) - 50.0f) < 0.01f);
  assert(porcentajeHumedadSuelo(3500, 2900, 1300) == 0.0f);    // más seco que la calibración
  assert(porcentajeHumedadSuelo(900, 2900, 1300) == 100.0f);   // más mojado
  assert(porcentajeHumedadSuelo(2000, 1500, 1500) < 0.0f);     // calibración inválida
}

static void prueba_codigo_y_mac() {
  assert(codigoValido("a1b2c3d4e5f6"));
  assert(codigoValido("A1B2C3D4E5F6"));
  assert(!codigoValido("a1b2c3d4e5f"));
  assert(!codigoValido("a1b2c3d4e5fg"));
  assert(!codigoValido(nullptr));

  char mac[13];
  assert(normalizarMac("24:6f:28:ab:12:34", mac) && std::strcmp(mac, "246F28AB1234") == 0);
  assert(normalizarMac("24-6F-28-AB-12-34", mac) && std::strcmp(mac, "246F28AB1234") == 0);
  assert(!normalizarMac("24:6F:28:AB:12", mac));
  assert(!normalizarMac("24:6F:28:AB:12:34:56", mac));
  assert(!normalizarMac("ZZ:6F:28:AB:12:34", mac));
}

static void prueba_qr() {
  char mac[13], codigo[13];
  assert(parsearQr("MAT:246F28AB1234:0a1b2c3d4e5f", mac, codigo));
  assert(std::strcmp(mac, "246F28AB1234") == 0 && std::strcmp(codigo, "0a1b2c3d4e5f") == 0);
  assert(parsearQr("MAT:24:6F:28:AB:12:34:0a1b2c3d4e5f", mac, codigo));
  assert(std::strcmp(mac, "246F28AB1234") == 0);
  assert(!parsearQr("XYZ:246F28AB1234:0a1b2c3d4e5f", mac, codigo));
  assert(!parsearQr("MAT:246F28AB1234:corto", mac, codigo));
  assert(!parsearQr("MAT::0a1b2c3d4e5f", mac, codigo));
}

static void prueba_urls() {
  char url[64];
  assert(unirUrl("https://192.168.1.5:5443/api/", "/lecturas", url, sizeof(url)));
  assert(std::strcmp(url, "https://192.168.1.5:5443/api/lecturas") == 0);
  assert(unirUrl("http://10.0.0.2:5001", "dispositivos/activar", url, sizeof(url)));
  assert(std::strcmp(url, "http://10.0.0.2:5001/dispositivos/activar") == 0);
  assert(!unirUrl("http://una-url-muy-larga-que-no-cabe.example.com", "/lecturas", url, 20));

  assert(urlBackendValida("http://192.168.1.5:5001"));
  assert(urlBackendValida("https://192.168.1.5:5443/api"));
  assert(!urlBackendValida("ftp://x"));
  assert(!urlBackendValida("http://"));
  assert(!urlBackendValida("192.168.1.5"));
}

static void prueba_pem() {
  const char* b64 =
      "MIIBszCCAVmgAwIBAgIUAAAAAAAAAAAAAAAAAAAAAAAAAAAwCgYIKoZIzj0EAwIwEDEOMAwGA1UEAwwF"
      "dGVzdDAeFw0yNjAxMDEwMDAwMDBaFw0zNjAxMDEwMDAwMDBa";
  char una_linea[512];
  std::snprintf(una_linea, sizeof(una_linea),
                "-----BEGIN CERTIFICATE----- %s -----END CERTIFICATE-----", b64);
  char salida[1024];
  assert(normalizarPemCertificado(una_linea, salida, sizeof(salida)));
  assert(std::strncmp(salida, "-----BEGIN CERTIFICATE-----\n", 28) == 0);
  // Primera línea de base64 envuelta a 64 columnas.
  assert(std::strncmp(salida + 28, b64, 64) == 0 && salida[28 + 64] == '\n');
  assert(std::strstr(salida, "\n-----END CERTIFICATE-----\n") != nullptr);

  char multilinea[512];
  std::snprintf(multilinea, sizeof(multilinea),
                "-----BEGIN CERTIFICATE-----\r\n%.40s\r\n%s\r\n-----END CERTIFICATE-----\r\n",
                b64, b64 + 40);
  char salida2[1024];
  assert(normalizarPemCertificado(multilinea, salida2, sizeof(salida2)));
  assert(std::strcmp(salida, salida2) == 0);

  assert(!normalizarPemCertificado("sin marcas", salida, sizeof(salida)));
  assert(!normalizarPemCertificado("-----BEGIN CERTIFICATE----- -----END CERTIFICATE-----", salida, sizeof(salida)));
  assert(!normalizarPemCertificado("-----BEGIN CERTIFICATE----- ab$c -----END CERTIFICATE-----", salida, sizeof(salida)));
  assert(!normalizarPemCertificado(una_linea, salida, 50));  // no cabe
}

int main() {
  prueba_porcentaje_suelo();
  prueba_codigo_y_mac();
  prueba_qr();
  prueba_urls();
  prueba_pem();
  std::puts("OK: todas las pruebas de logica.h pasaron");
  return 0;
}
