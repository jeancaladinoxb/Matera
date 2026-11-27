#pragma once

#include <Arduino.h>

#include "almacenamiento.h"

// Qué cambió tras procesar un comando, para que el programa principal reaccione.
struct EventosConsola {
  bool reconectarWifi = false;
  bool reiniciarActivacion = false;
  bool leerAhora = false;
};

namespace consola {

void mostrarAyuda();
void mostrarEstado(const ConfigMatera& config, const char* mac);
// Lee el monitor serie sin bloquear y ejecuta comandos completos.
EventosConsola procesar(ConfigMatera& config, const char* mac);

}  // namespace consola
