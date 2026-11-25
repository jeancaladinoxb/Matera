#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APP_SUPPORT_DIR="${HOME}/Library/Application Support/CuidaTuMate"
NGINX_CONF="${APP_SUPPORT_DIR}/nginx.conf"
CERT_FILE="${APP_SUPPORT_DIR}/localhost.pem"
KEY_FILE="${APP_SUPPORT_DIR}/localhost-key.pem"
CA_CERT="$(mkcert -CAROOT)/rootCA.pem"
NGINX_BIN="$(brew --prefix nginx)/bin/nginx"
MIME_TYPES="$(brew --prefix)/etc/nginx/mime.types"
FLASK_BIN="${ROOT_DIR}/.venv/bin/flask"
VITE_BIN="${ROOT_DIR}/frontend/node_modules/.bin/vite"
PG_ISREADY_BIN="$(command -v pg_isready || true)"
CHECK_ONLY=false
started_pids=()

if [[ "${1:-}" == "--check" ]]; then
  CHECK_ONLY=true
elif [[ $# -gt 0 ]]; then
  printf 'Uso: %s [--check]\n' "$0" >&2
  exit 2
fi

for command_name in awk brew curl ipconfig lsof mkcert route; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Falta el comando requerido: %s\n' "$command_name" >&2
    exit 1
  fi
done

if [[ ! -x "$NGINX_BIN" || ! -r "$MIME_TYPES" || ! -x "$FLASK_BIN" || ! -x "$VITE_BIN" ]]; then
  printf 'Falta Nginx, sus tipos MIME, Flask del entorno virtual o Vite del frontend.\n' >&2
  exit 1
fi

if [[ -z "$PG_ISREADY_BIN" ]]; then
  printf 'Falta pg_isready; instala o habilita el cliente de PostgreSQL.\n' >&2
  exit 1
fi

DEFAULT_INTERFACE="$(route -n get default 2>/dev/null | awk '/interface:/{print $2; exit}' || true)"
if [[ -z "$DEFAULT_INTERFACE" ]]; then
  printf 'No se pudo detectar la interfaz de red predeterminada.\n' >&2
  exit 1
fi

LAN_IP="$(ipconfig getifaddr "$DEFAULT_INTERFACE" 2>/dev/null || true)"
if [[ ! "$LAN_IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
  printf 'No se pudo obtener una IPv4 local para la interfaz %s.\n' "$DEFAULT_INTERFACE" >&2
  exit 1
fi

mkdir -p "$APP_SUPPORT_DIR"

mkcert \
  -cert-file "$CERT_FILE" \
  -key-file "$KEY_FILE" \
  localhost "$LAN_IP"
chmod 600 "$KEY_FILE"

cat >"$NGINX_CONF" <<EOF
worker_processes 1;
error_log "${APP_SUPPORT_DIR}/nginx-error.log" info;
pid "${APP_SUPPORT_DIR}/nginx.pid";

events {
    worker_connections 128;
}

http {
    include "${MIME_TYPES}";
    default_type application/octet-stream;

    map \$http_upgrade \$connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen ${LAN_IP}:5443 ssl;
        server_name ${LAN_IP};

        ssl_certificate "${CERT_FILE}";
        ssl_certificate_key "${KEY_FILE}";
        ssl_protocols TLSv1.2 TLSv1.3;
        server_tokens off;

        location /api/ {
            proxy_pass http://127.0.0.1:5001/;
            proxy_set_header Host \$host;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location / {
            proxy_pass http://127.0.0.1:5173;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection \$connection_upgrade;
            proxy_set_header Host \$host;
            proxy_read_timeout 1h;
        }
    }
}
EOF

"$NGINX_BIN" -p "${APP_SUPPORT_DIR}/" -c "$NGINX_CONF" -t

if [[ "$CHECK_ONLY" == true ]]; then
  printf 'Configuración HTTPS local válida: https://%s:5443\n' "$LAN_IP"
  exit 0
fi

for port in 5001 5173 5443; do
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    printf 'El puerto %s ya está en uso; no se detuvo ningún proceso.\n' "$port" >&2
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >&2 || true
    if [[ "$port" == 5001 ]]; then
      printf 'Detén manualmente el backend existente y vuelve a ejecutar este script.\n' >&2
    fi
    exit 1
  fi
done

if ! "$PG_ISREADY_BIN" -h 127.0.0.1 -p "${DB_PORT:-5432}" -q; then
  printf 'PostgreSQL no responde en 127.0.0.1:%s; inicia la base de datos y reintenta.\n' \
    "${DB_PORT:-5432}" >&2
  exit 1
fi

cleanup() {
  local exit_status=$?
  trap - EXIT INT TERM

  for pid in "${started_pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done
  for pid in "${started_pids[@]}"; do
    wait "$pid" 2>/dev/null || true
  done

  exit "$exit_status"
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local pid="$3"
  local ca_file="${4:-}"
  local -a curl_options
  local attempt

  curl_options=(--silent --show-error --max-time 1 --output /dev/null)
  if [[ -n "$ca_file" ]]; then
    curl_options+=(--cacert "$ca_file")
  fi

  for ((attempt = 0; attempt < 40; attempt++)); do
    if curl "${curl_options[@]}" "$url" 2>/dev/null; then
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      printf '%s terminó antes de responder: %s\n' "$name" "$url" >&2
      return 1
    fi
    sleep 0.5
  done

  printf '%s no respondió a tiempo: %s\n' "$name" "$url" >&2
  return 1
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

cd "$ROOT_DIR"
APP_ENV=development \
SESSION_COOKIE_SECURE=true \
SESSION_COOKIE_SAMESITE=Lax \
  "$FLASK_BIN" --app backend.app:create_app run \
    --host 127.0.0.1 --port 5001 --no-reload &
flask_pid=$!
started_pids+=("$flask_pid")

wait_for_http "Backend Flask" "http://127.0.0.1:5001/panel" "$flask_pid"

cd "${ROOT_DIR}/frontend"
MATERA_HTTPS_DEV=true \
MATERA_HTTPS_HOST="$LAN_IP" \
VITE_API_BASE_URL="https://${LAN_IP}:5443/api" \
  "$VITE_BIN" --host 127.0.0.1 --port 5173 --strictPort &
vite_pid=$!
started_pids+=("$vite_pid")

wait_for_http "Frontend Vite" "http://127.0.0.1:5173/" "$vite_pid"

"$NGINX_BIN" -p "${APP_SUPPORT_DIR}/" -c "$NGINX_CONF" -g "daemon off;" &
nginx_pid=$!
started_pids+=("$nginx_pid")

wait_for_http \
  "Proxy Nginx" \
  "https://${LAN_IP}:5443/" \
  "$nginx_pid" \
  "$CA_CERT"
printf 'Aplicación disponible en https://%s:5443\n' "$LAN_IP"
printf 'Presiona Ctrl+C para detener solo los procesos iniciados por este script.\n'

wait "$nginx_pid"
