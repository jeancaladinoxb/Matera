#pragma once

#include <Arduino.h>

struct Lectura {
  bool sueloOk;
  int sueloCrudo;
  float humedadSuelo;   // %

  bool temperaturaOk;
  float temperatura;    // °C
  bool humedadAireOk;
  float humedadAire;    // %

  bool luzOk;
  float luzLux;         // lux
};

namespace sensores {

void iniciar();
// Lee los tres sensores. Un sensor que falla queda marcado con *Ok = false
// y se envía como null al backend, sin bloquear a los demás.
Lectura leer(int sueloCrudoSeco, int sueloCrudoMojado);
// Promedio de lecturas crudas del sensor de suelo, para calibrar.
int leerSueloCrudo();
bool hayMedidorDeLuz();

}  // namespace sensores
