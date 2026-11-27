#pragma once

// ---------------------------------------------------------------------------
// Configuración de hardware y tiempos. Cambia los pines aquí si tu montaje es
// distinto. WiFi, backend y código de vinculación NO van aquí: se configuran
// por el monitor serie y quedan guardados en la memoria del ESP32 (NVS), para
// no subir secretos al repositorio.
// ---------------------------------------------------------------------------

// Humedad del suelo: sensor capacitivo v1.2 (salida analógica).
// Debe ser un pin del ADC1 (GPIO32-39): el ADC2 no funciona con WiFi activo.
#define PIN_HUMEDAD_SUELO 34

// Temperatura (y humedad del aire): DHT22 / AM2302.
#define PIN_DHT 4
#define TIPO_DHT DHT22

// Luz: BH1750 por I2C (mide directamente en lux).
#define PIN_SDA 21
#define PIN_SCL 22

// Calibración por defecto del sensor de humedad del suelo (lecturas crudas del
// ADC de 12 bits). Se recomienda calibrar con los comandos `calibrar seco` y
// `calibrar mojado`; estos valores solo se usan si no hay calibración guardada.
#define SUELO_CRUDO_SECO_DEFECTO 2900
#define SUELO_CRUDO_MOJADO_DEFECTO 1300
#define MUESTRAS_SUELO 10

// Tiempos.
#define INTERVALO_LECTURAS_DEFECTO_S 60    // cada cuánto se envía una lectura
#define INTERVALO_MINIMO_S 10
#define REINTENTO_ACTIVACION_S 30           // mientras el usuario no vincule la matera
#define REINTENTO_WIFI_S 15
#define TIMEOUT_HTTP_MS 8000

#define VERSION_FIRMWARE "1.0.0"
