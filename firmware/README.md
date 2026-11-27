# Firmware ESP32 — Matera Inteligente

Lee humedad del suelo, temperatura, humedad del aire y luz. Se activa contra el
backend con `POST /dispositivos/activar` y envía lecturas periódicas a
`POST /lecturas` con su JWT de dispositivo.

## Hardware y conexiones

| Sensor | Pin del sensor | ESP32 |
| --- | --- | --- |
| Humedad del suelo capacitivo v1.2 | AOUT | GPIO34 |
| | VCC / GND | 3V3 / GND |
| DHT22 (temperatura y humedad del aire) | DATA | GPIO4 (con pull-up de 10 kΩ si el módulo no lo trae) |
| | VCC / GND | 3V3 / GND |
| BH1750 (luz en lux) | SDA / SCL | GPIO21 / GPIO22 |
| | VCC / GND | 3V3 / GND |

Los pines se cambian en `matera_esp32/config.h`. El sensor de suelo debe ir en
un pin del ADC1 (GPIO32–39), porque el ADC2 no funciona con el WiFi activo.

## Compilar y cargar

**Arduino IDE:** instala la placa *esp32* de Espressif y las librerías
*DHT sensor library* (Adafruit), *Adafruit Unified Sensor*, *BH1750* (claws) y
*ArduinoJson* 7. Abre `matera_esp32/matera_esp32.ino`, elige *ESP32 Dev Module*
y carga.

**PlatformIO:** desde `firmware/`, `pio run -t upload` y luego `pio device monitor`.

## Primera configuración (monitor serie a 115200, fin de línea "Nueva línea")

1. Registra la MAC en el backend con el CLI de fábrica (imprime `MAT:<MAC>:<CODIGO>`):
   ```
   python -m backend.materas.cli <MAC_DEL_ESP32>
   ```
   La MAC sale al arrancar el ESP32 o con el comando `estado`.
2. En el monitor serie:
   ```
   setssid MiRedWifi
   setclave miClave
   setbackend http://192.168.1.10:5001
   setqr MAT:<MAC>:<CODIGO>
   ```
3. Vincula la matera en la web con la misma MAC y código. El ESP32 reintenta la
   activación cada 30 s; al lograrlo guarda el token y empieza a enviar lecturas.

Todo queda guardado en la memoria del ESP32; no hay claves en el código.

### HTTPS (`https://<IP>:5443/api` con `scripts/dev-https.sh`)

```
setbackend https://192.168.78.154:5443/api
setca
```
Después de `setca`, pega el contenido de `rootCA.pem` (ruta: `mkcert -CAROOT`).
Es el certificado **público** de la CA; nunca pegues ni compartas `rootCA-key.pem`.
El firmware no desactiva la validación del certificado.

Si usas `http://`, Flask debe escuchar en la red (`--host 0.0.0.0`), porque
`dev-https.sh` lo deja solo en `127.0.0.1`.

### Calibrar el sensor de suelo

Con el sensor limpio y al aire, `calibrar seco`; luego dentro de un vaso de agua
(sin mojar la parte electrónica), `calibrar mojado`.

## Contrato de lecturas (pendiente en el backend)

```
POST /lecturas
Authorization: Bearer <JWT del dispositivo>
Content-Type: application/json

{"humedad_suelo": 42.5, "temperatura": 21.3, "humedad_aire": 58.0, "luz_lux": 5320.0}
```

- Unidades: % de humedad del suelo, °C, % de humedad del aire y lux (las mismas
  de los rangos de la tabla `plantas`).
- Un sensor que falla se envía como `null`.
- La MAC no viaja en el cuerpo: el backend la toma del claim `sub` del JWT.
- La hora la pone el servidor al recibir la lectura.
- Respuestas esperadas: `201` creada, `401` token inválido (el ESP32 se vuelve a
  activar). Mientras el endpoint no exista, el ESP32 recibe `404`, lo avisa por
  el monitor serie y sigue funcionando.

## Pruebas de la lógica en el PC

```
cd firmware/pruebas_pc
g++ -std=c++17 -Wall -Wextra -I../matera_esp32 test_logica.cpp -o test_logica && ./test_logica
```
