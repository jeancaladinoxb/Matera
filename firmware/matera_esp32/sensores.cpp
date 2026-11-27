#include "sensores.h"

#include <BH1750.h>
#include <DHT.h>
#include <Wire.h>

#include "config.h"
#include "logica.h"

namespace {

DHT dht(PIN_DHT, TIPO_DHT);
BH1750 medidorLuz;
bool medidorLuzListo = false;

}  // namespace

namespace sensores {

void iniciar() {
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_HUMEDAD_SUELO, ADC_11db);  // rango ~0-3.1 V
  pinMode(PIN_HUMEDAD_SUELO, INPUT);

  dht.begin();

  Wire.begin(PIN_SDA, PIN_SCL);
  medidorLuzListo = medidorLuz.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  if (!medidorLuzListo) {
    Serial.println(F("[sensores] No se detectó el BH1750: la luz se enviará como null."));
  }
}

int leerSueloCrudo() {
  long suma = 0;
  for (int i = 0; i < MUESTRAS_SUELO; i++) {
    suma += analogRead(PIN_HUMEDAD_SUELO);
    delay(10);
  }
  return (int)(suma / MUESTRAS_SUELO);
}

bool hayMedidorDeLuz() { return medidorLuzListo; }

Lectura leer(int sueloCrudoSeco, int sueloCrudoMojado) {
  Lectura lectura = {};

  // Humedad del suelo. Un valor crudo de 0 o 4095 suele indicar sensor
  // desconectado o en corto.
  lectura.sueloCrudo = leerSueloCrudo();
  float porcentaje =
      logica::porcentajeHumedadSuelo(lectura.sueloCrudo, sueloCrudoSeco, sueloCrudoMojado);
  lectura.sueloOk =
      lectura.sueloCrudo > 0 && lectura.sueloCrudo < 4095 && porcentaje >= 0.0f;
  lectura.humedadSuelo = lectura.sueloOk ? porcentaje : 0.0f;

  // Temperatura y humedad del aire (DHT22; necesita >= 2 s entre lecturas).
  float temperatura = dht.readTemperature();
  float humedadAire = dht.readHumidity();
  lectura.temperaturaOk = !isnan(temperatura);
  lectura.temperatura = lectura.temperaturaOk ? temperatura : 0.0f;
  lectura.humedadAireOk = !isnan(humedadAire);
  lectura.humedadAire = lectura.humedadAireOk ? humedadAire : 0.0f;

  // Luz en lux (BH1750 devuelve un valor negativo si falla).
  if (medidorLuzListo) {
    float lux = medidorLuz.readLightLevel();
    lectura.luzOk = lux >= 0.0f;
    lectura.luzLux = lectura.luzOk ? lux : 0.0f;
  }

  return lectura;
}

}  // namespace sensores
