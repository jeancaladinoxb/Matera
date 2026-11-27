// Firmware de la Matera Inteligente (ESP32)
//
// Sensores: humedad del suelo (capacitivo v1.2), temperatura y humedad del aire
// (DHT22) y luz en lux (BH1750).
//
// Flujo:
//   1. Se configura por el monitor serie (115200 baudios): WiFi, URL del
//      backend y código de vinculación (comando `ayuda`).
//   2. El usuario vincula la matera en la web con la MAC y el código.
//   3. El ESP32 llama a POST /dispositivos/activar y guarda su JWT.
//   4. Cada `intervalo` segundos lee los sensores y hace POST /lecturas con
//      el JWT en la cabecera Authorization.

#include "app.h"

void setup() { app::iniciar(); }

void loop() { app::ciclo(); }
