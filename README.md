# Gestión de usuarios

Backend para registro e inicio de sesión de usuarios, construido con
arquitectura hexagonal. La aplicación expone una API HTTP con Flask, persiste
usuarios en PostgreSQL, hashea contraseñas con Argon2 y entrega tokens JWT.

## Arquitectura

Las dependencias apuntan hacia adentro: `infrastructure` conoce y conecta los
puertos de `application`; `application` depende de `domain`; el dominio no
depende de Flask, PostgreSQL ni de librerías externas.

- **`domain`**: entidad `Usuario`, objetos de valor `Email` y `Password`, y
  errores/reglas de negocio.
- **`application`**: puertos de entrada y salida e implementación de los casos
  de uso de registro e inicio de sesión. Recibe dependencias por constructor.
- **`infrastructure`**: adaptadores de PostgreSQL, Argon2 y JWT, y controlador
  Flask que traduce solicitudes y errores a HTTP.
- **`backend/app.py`**: composición de adaptadores, casos de uso y controlador;
  carga la configuración de `backend/.env`.

Estructura relevante del proyecto:

```text
.
├── backend/
│   ├── app.py
│   ├── .env.example
│   ├── dev_tools/
│   │   └── test_page.html
│   ├── tests/
│   │   └── test_app.py
│   └── usuarios/
│       ├── domain/
│       │   ├── email.py
│       │   ├── errors.py
│       │   ├── password.py
│       │   └── usuario.py
│       ├── application/
│       │   ├── ports/
│       │   │   ├── errors.py
│       │   │   ├── input/
│       │   │   └── output/
│       │   └── use_cases/
│       ├── infrastructure/
│       │   ├── adapters/
│       │   └── controllers/
│       └── tests/
├── db/
│   └── 001_usuarios.sql
├── pytest.ini
├── requirements.txt
└── README.md
```

## Reglas de negocio

- El correo debe tener formato válido y se normaliza al quitar espacios al
  principio/final y convertirlo a minúsculas.
- La contraseña debe tener al menos 8 caracteres, ser alfanumérica y contener
  al menos una mayúscula.
- El correo es único. La restricción `UNIQUE` de PostgreSQL es la garantía
  definitiva también cuando hay registros simultáneos.
- Las contraseñas nunca se almacenan en texto plano: se guardan usando Argon2.
- El nickname no tiene restricción de unicidad en la base de datos.

## Requisitos

- Python 3.9.
- PostgreSQL.

## Instalación y ejecución

Desde la raíz del repositorio:

1. Crea y activa un entorno virtual e instala las dependencias:

   ```bash
   python3.9 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

2. Crea la base de datos PostgreSQL. Por ejemplo:

   ```bash
   createdb matera
   ```

3. Crea la tabla ejecutando el script:

   ```bash
   psql -d matera -f db/001_usuarios.sql
   ```

4. Copia el ejemplo de configuración y completa `backend/.env` localmente:

   ```bash
   cp backend/.env.example backend/.env
   ```

   Configura `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` para tu
   PostgreSQL. Configura `JWT_SECRET` con un valor secreto de al menos 32
   caracteres. Puedes generar uno con:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   `JWT_EXPIRATION_HOURS` es obligatoria para el arranque; configura `5` para
   tokens de cinco horas. El `.env` está excluido de Git; no lo compartas ni lo
   agregues a commits.

5. Inicia la aplicación con la página de prueba habilitada:

   ```bash
   APP_ENV=development ./.venv/bin/python -m backend.app
   ```

   La configuración actual de `backend/app.py` sirve en el puerto `5001`.
   Para usar el comando de Flask CLI y especificar el puerto explícitamente:

   ```bash
   APP_ENV=development ./.venv/bin/flask --app backend.app:create_app run --port 5001
   ```

   En macOS, el puerto `5000` suele estar ocupado por AirPlay Receiver; se
   recomienda usar `--port 5001`.

## API

### `POST /registro`

Registra un usuario e inicia su sesión. Ejemplo de JSON:

```json
{
  "nombre": "Ana",
  "apellido": "Pérez",
  "nickname": "anap",
  "correo": "ana@example.com",
  "contrasena": "Clave123"
}
```

### `POST /login`

Inicia sesión con correo y contraseña. Ejemplo de JSON:

```json
{
  "correo": "ana@example.com",
  "contrasena": "Clave123"
}
```

En ambos casos, una respuesta exitosa tiene la forma:

```json
{"token": "<JWT>"}
```

| Código HTTP | Significado |
|---|---|
| `201` | Registro exitoso |
| `200` | Inicio de sesión exitoso |
| `400` | JSON/campos inválidos, reglas de validación o registro no completado |
| `401` | Credenciales de inicio de sesión inválidas |
| `500` | Error interno genérico |

El duplicado de correo durante el registro responde `400` con el mensaje
genérico `No se pudo completar el registro`. Los errores de inicio de sesión
responden `401` con un mensaje genérico.

Ejemplo de registro con `curl` (usa un correo de prueba que no esté registrado):

```bash
curl -i -X POST http://127.0.0.1:5001/registro \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","apellido":"Pérez","nickname":"anap","correo":"ana@example.com","contrasena":"Clave123"}'
```

Para iniciar sesión:

```bash
curl -i -X POST http://127.0.0.1:5001/login \
  -H 'Content-Type: application/json' \
  -d '{"correo":"ana@example.com","contrasena":"Clave123"}'
```

El JWT contiene `sub` como el ID del usuario convertido a texto; no identifica
al usuario por correo. Incluye `iat` y `exp`, y su duración se configura con
`JWT_EXPIRATION_HOURS` (usa `5` para cinco horas). El cliente debe tratarlo
como bearer token y enviarlo en `Authorization: Bearer <JWT>` a las rutas que
requieran autenticación. Actualmente registro e inicio de sesión son las rutas
expuestas; no hay todavía rutas protegidas.

## Página de prueba

Con `APP_ENV=development` o `FLASK_DEBUG=1`, abre
[`http://127.0.0.1:5001/dev/test`](http://127.0.0.1:5001/dev/test) para probar
registro e inicio de sesión desde formularios. La ruta no se registra en modo
de producción. El token se muestra en pantalla y la página no lo persiste.

## Pruebas

Las pruebas unitarias no usan Flask real ni PostgreSQL en los casos de uso;
emplean fakes o el test client. Para ejecutar las pruebas que no son de
integración:

```bash
pytest -m "not integration"
```

Las pruebas de integración PostgreSQL están marcadas `integration` y requieren
`TEST_DATABASE_URL` apuntando a una base de datos **de pruebas** con el esquema
creado. Estas pruebas insertan y eliminan filas de prueba:

```bash
export TEST_DATABASE_URL='postgresql://USUARIO:CONTRASENA@HOST:5432/BASE_DE_PRUEBAS'
pytest -m integration
```

Sin `TEST_DATABASE_URL`, las tres pruebas de integración se omiten. No apuntes
esta variable a una base de producción.

## Decisiones de diseño

- El JWT identifica al usuario por ID (`sub`), no por correo.
- El inicio de sesión responde de forma genérica tanto si el correo no existe
  como si la contraseña no coincide.
- La comprobación previa del correo en el caso de uso mejora el flujo normal,
  pero la restricción `UNIQUE` es la que evita duplicados ante solicitudes
  simultáneas.
- Un hash de Argon2 inválido o dañado produce una verificación fallida y se
  registra en el log únicamente el tipo de error, sin contraseña, hash ni otros
  datos sensibles.

## Limitaciones conocidas y trabajo futuro

- Agregar límite de intentos de inicio de sesión y protección contra fuerza
  bruta.
- Definir refresh tokens.
- Aunque el duplicado responde con un mensaje genérico, una solicitud de
  registro válida que recibe `400` puede permitir inferir que el correo ya
  estaba registrado.
- Agregar verificación de correo y recuperación de contraseña.


