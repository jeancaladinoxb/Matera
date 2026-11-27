#include "almacenamiento.h"

#include <Preferences.h>

#include "config.h"

namespace {

const char* const NAMESPACE = "matera";

void guardarTexto(const char* clave, const String& valor) {
  Preferences prefs;
  prefs.begin(NAMESPACE, false);
  prefs.putString(clave, valor);
  prefs.end();
}

}  // namespace

namespace almacenamiento {

void cargar(ConfigMatera& config) {
  Preferences prefs;
  prefs.begin(NAMESPACE, true);
  config.ssid = prefs.getString("ssid", "");
  config.claveWifi = prefs.getString("clave", "");
  config.urlBackend = prefs.getString("backend", "");
  config.codigo = prefs.getString("codigo", "");
  config.token = prefs.getString("token", "");
  config.certificadoCa = prefs.getString("ca", "");
  config.sueloCrudoSeco = prefs.getInt("seco", SUELO_CRUDO_SECO_DEFECTO);
  config.sueloCrudoMojado = prefs.getInt("mojado", SUELO_CRUDO_MOJADO_DEFECTO);
  config.intervaloS = prefs.getUInt("intervalo", INTERVALO_LECTURAS_DEFECTO_S);
  prefs.end();
}

void guardarWifi(const String& ssid, const String& clave) {
  guardarSsid(ssid);
  guardarClaveWifi(clave);
}

void guardarSsid(const String& ssid) { guardarTexto("ssid", ssid); }
void guardarClaveWifi(const String& clave) { guardarTexto("clave", clave); }
void guardarUrlBackend(const String& url) { guardarTexto("backend", url); }
void guardarCodigo(const String& codigo) { guardarTexto("codigo", codigo); }
void guardarToken(const String& token) { guardarTexto("token", token); }
void guardarCertificadoCa(const String& pem) { guardarTexto("ca", pem); }

void borrarToken() {
  Preferences prefs;
  prefs.begin(NAMESPACE, false);
  prefs.remove("token");
  prefs.end();
}

void guardarCalibracion(int crudoSeco, int crudoMojado) {
  Preferences prefs;
  prefs.begin(NAMESPACE, false);
  prefs.putInt("seco", crudoSeco);
  prefs.putInt("mojado", crudoMojado);
  prefs.end();
}

void guardarIntervalo(uint32_t segundos) {
  Preferences prefs;
  prefs.begin(NAMESPACE, false);
  prefs.putUInt("intervalo", segundos);
  prefs.end();
}

void borrarTodo() {
  Preferences prefs;
  prefs.begin(NAMESPACE, false);
  prefs.clear();
  prefs.end();
}

}  // namespace almacenamiento
