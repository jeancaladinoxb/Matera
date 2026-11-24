# Cuida tu mate

Cuida tu mate es una aplicación web completa para el registro e inicio de
sesión de usuarios, la gestión de sesiones y la vinculación de materas
inteligentes. El proyecto combina una API HTTP construida con Flask y un
frontend React construido con arquitectura hexagonal.

## ¿Qué hace la aplicación?

- Permite registrar usuarios con validación de nombre, apellido, nickname,
  correo electrónico y contraseña.
- Permite iniciar sesión con mensajes genéricos y seguros ante errores de
  credenciales.
- Mantiene la sesión en una cookie `HttpOnly` emitida por el backend.
- Vincula materas físicas mediante escaneo QR o ingreso manual de MAC y código.
- Consulta si el usuario ya tiene una matera vinculada después del inicio de
  sesión y protege la ruta de vinculación.
- Permite omitir la vinculación mediante la opción "Más tarde".
- Renueva automáticamente el JWT cada 15 minutos sin interrumpir al usuario.
- Reintenta los refrescos afectados por problemas de red mediante backoff
  exponencial.
- Permite cerrar sesión y expirar la cookie desde el frontend.
- Vincula materas físicas mediante MAC y código de reclamo.
- Activa dispositivos asociados con tokens JWT específicos para dispositivos.
- Expone el panel principal del usuario con sus datos y todas sus materas
  vinculadas.
- Incluye pantallas móviles y de escritorio con modo claro y modo oscuro,
  validación en vivo, estados de carga y mensajes accesibles.

## Tecnologías

### Backend

- Python 3.9 o superior
- Flask
- PostgreSQL y `psycopg2`
- Argon2
- PyJWT
- pytest
- Python-dotenv
- Arquitectura hexagonal

### Frontend

- React
- TypeScript
- Vite
- React Router
- Vitest
- `html5-qrcode`
- Fetch API
- CSS con variables de diseño, `backdrop-filter` y animaciones
- Arquitectura hexagonal con dominio, aplicación e infraestructura

## Requisitos del sistema

### Herramientas necesarias

- macOS, Linux o Windows con WSL
- Python 3.9 o superior
- PostgreSQL 13 o superior
- Node.js 20 o superior
- npm
- Git

### Variables de configuración

Los archivos de entorno están excluidos por Git y no deben subirse al
repositorio.

Variables mínimas del backend:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `JWT_SECRET`
- `JWT_EXPIRATION_HOURS`
- `CLAIM_MASTER_KEY`
- `DEVICE_JWT_SECRET`
- `DEVICE_JWT_EXPIRATION_DAYS`
- `CORS_ALLOWED_ORIGINS`
- `SESSION_COOKIE_SECURE`
- `SESSION_COOKIE_SAMESITE`
- `SESSION_COOKIE_NAME`

Variables del frontend:

- `VITE_API_BASE_URL`
- `VITE_HTTP_TIMEOUT_MS`

Se incluye `frontend/.env.example` como plantilla local sin secretos.

## Arquitectura

Las dependencias apuntan hacia adentro:

- **Dominio**: entidades, objetos de valor y reglas de negocio. No importa
  Flask, PostgreSQL, Fetch ni React.
- **Aplicación**: puertos de entrada y salida y casos de uso. No conoce HTTP,
  cookies ni componentes de interfaz.
- **Infraestructura**: adaptadores Flask/HTTP, composición, repositorios,
  componentes React y configuración.
- **Composición**: `frontend/usuarios/infraestructura/composicion/composicion-root.ts`
  instancia adaptadores y casos de uso.

## Instalación

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Crear una base de datos PostgreSQL y ejecutar los scripts:

```bash
createdb matera
psql -d matera -f db/001_usuarios.sql
psql -d matera -f db/002_materas.sql
```

Crear `backend/.env` localmente con las variables necesarias. Para desarrollo,
permitir los orígenes locales de Vite en `CORS_ALLOWED_ORIGINS`. No se deben
registrar archivos `.env` en Git ni incluir secretos en ejemplos o commits.

Instalar el frontend:

```bash
cd frontend
npm install
cp .env.example .env
```

## Ejecución

### Backend

Desde la raíz del proyecto:

```bash
APP_ENV=development ./.venv/bin/python -m backend.app
```

El backend escucha en `http://localhost:5001`.

También puede iniciarse con Flask CLI:

```bash
APP_ENV=development ./.venv/bin/flask --app backend.app:create_app run --port 5001
```

### Frontend

Desde `frontend/`:

```bash
npm run dev
```

Vite normalmente abre `http://localhost:5173`.

## API de usuarios

### `POST /registro`

Registra un usuario sin iniciar sesión.

```json
{
  "nombre": "Ana",
  "apellido": "Pérez",
  "nickname": "anap",
  "correo": "ana@example.com",
  "contrasena": "Clave123"
}
```

Responde `201` con un mensaje de éxito.

### `POST /login`

Inicia sesión y establece la cookie de sesión `HttpOnly`.

```json
{
  "correo": "ana@example.com",
  "contrasena": "Clave123"
}
```

Responde `200` y guarda el JWT en la cookie configurada. El frontend no lee ni
guarda el JWT en JavaScript.

### `POST /session/refresh`

Renueva el JWT mientras la cookie siga siendo válida. Responde `200` al
renovar o `401` si el backend rechaza explícitamente la sesión.

### `POST /logout`

Cierra la sesión y expira la cookie. Responde `204`.

## API de materas

### `POST /materas/vincular`

Vincula una matera al usuario autenticado por cookie. El cuerpo contiene la
dirección MAC y el código de vinculación:

```json
{
  "mac": "24:6F:28:AB:12:34",
  "codigo": "9f3a1c7e0b52"
}
```

Respuestas principales:

- `200`: matera vinculada.
- `400`: MAC, código o cuerpo inválido.
- `401`: sesión vencida o cookie ausente.
- `404`: matera inexistente o código inválido.
- `409`: la matera ya está vinculada.
- `500`: error interno genérico.

Este endpoint ya no requiere ni acepta un JWT de usuario en `Authorization`.
La autenticación se obtiene exclusivamente de la cookie `HttpOnly` configurada
por el backend.

### `GET /materas/mias`

Consulta si el usuario autenticado tiene una matera vinculada.

```json
{
  "vinculada": true,
  "mac": "246F28AB1234"
}
```

Cuando no existe una vinculación responde:

```json
{
  "vinculada": false,
  "mac": null
}
```

### `POST /dispositivos/activar`

Permite activar una matera ya vinculada. Recibe MAC y código y devuelve un JWT
exclusivo para el dispositivo ESP32.

## Panel principal

### `GET /panel`

Consulta el perfil y las materas vinculadas del usuario autenticado. La
identidad se obtiene de la cookie de sesión `HttpOnly`; el endpoint no acepta
un `usuario_id` enviado por el cliente.

Respuesta `200`:

```json
{
  "usuario": {
    "usuario_id": 7,
    "nombre": "Ana",
    "nickname": "anap"
  },
  "materas": [
    {
      "matera_id": 12,
      "dispositivo_id": 12,
      "mac": "246F28AB1234",
      "planta_id": null
    }
  ]
}
```

La respuesta incluye todas las materas vinculadas al usuario. `dispositivo_id`
usa actualmente el mismo identificador que `matera_id`. Una lista `materas`
vacía es válida. `planta_id` es `null` mientras no haya una asignación de planta.
El panel todavía no devuelve lecturas de sensores.

Respuestas principales:

- `401`: cookie ausente o sesión inválida.
- `404`: usuario de la sesión no encontrado.
- `500`: error interno genérico.

## Reglas de validación

- El correo se recorta y convierte a minúsculas.
- El correo debe tener formato válido y una longitud máxima de 254 caracteres.
- La contraseña debe tener al menos 8 caracteres.
- La contraseña debe ser alfanumérica y contener al menos una mayúscula.
- Nombre, apellido y nickname son obligatorios.
- Los errores de credenciales son genéricos para no revelar si falló el correo
  o la contraseña.
- Los errores de registro y duplicados no revelan detalles innecesarios.

## Sesión y seguridad

- Login y refresh usan `credentials: "include"` en el frontend.
- Vinculación y consulta de materas usan la misma cookie de sesión mediante
  `credentials: "include"`; el código de vinculación nunca se guarda en
  `localStorage`, URL ni logs.
- La cookie es `HttpOnly`, por lo que JavaScript no puede leerla ni escribirla.
- `Secure` se activa por defecto en producción.
- CORS usa una lista explícita de orígenes configurados por entorno.
- El uso del comodín `*` con credenciales no está permitido.
- Las contraseñas se almacenan mediante Argon2.
- Los secretos, contraseñas y archivos de entorno deben mantenerse fuera del
  control de versiones.

## Gestión de materas

El módulo `backend/materas/` mantiene las mismas capas hexagonales. El frontend
también usa capas `dominio`, `aplicacion` e `infraestructura` dentro de
`frontend/materas/`.

- Una MAC se normaliza a doce caracteres hexadecimales en mayúsculas.
- Una MAC acepta separadores `:`, `-` o `.` y se convierte sin separadores.
- El código de vinculación debe tener exactamente 12 caracteres hexadecimales.
- El texto QR tiene el formato `MAT:<MAC>:<codigo>`.
- El frontend ofrece escaneo con cámara y entrada manual.
- El escaneo usa `html5-qrcode` y requiere HTTPS o `localhost` en el navegador.
- Tras iniciar sesión, la aplicación consulta `/materas/mias`.
- Si no existe una vinculación, redirige a `/materas/vincular`.
- “Más tarde” permite continuar sin vincular a `/inicio`.
- El código se deriva con HMAC-SHA256 usando la clave maestra.
- `POST /materas/vincular` vincula una matera a un usuario autenticado.
- `POST /dispositivos/activar` entrega un token JWT exclusivo para el dispositivo.

El módulo `backend/panelPrincipal/` implementa el endpoint del panel con capas
de dominio, aplicación e infraestructura. Sus consultas PostgreSQL son de solo
lectura y filtran las materas por el `usuario_id` autenticado.

## Pruebas

Ejecutar las pruebas de backend:

```bash
./.venv/bin/python -m pytest -q
```

Ejecutar las pruebas de frontend:

```bash
cd frontend
npm test
npm run typecheck
npm run build
```

Las pruebas de integración PostgreSQL requieren `TEST_DATABASE_URL` y una base
de datos exclusiva para pruebas. Si no está configurada, pueden omitirse
correctamente.

## Rutas del frontend

- `/registro`: formulario de creación de cuenta.
- `/login`: formulario de inicio de sesión.
- `/inicio`: pantalla principal mínima y cierre de sesión.
- `/materas/vincular`: vinculación mediante cámara QR o datos manuales.

El proyecto usa React Router y admite navegación directa a esas rutas.
