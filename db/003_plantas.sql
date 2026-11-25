-- Requiere db/001_usuarios.sql y db/002_materas.sql (agrega una clave foránea en materas).
--
-- PROVISIONAL: los rangos ideales de humedad del suelo (%), temperatura (°C) y luz (lux) de
-- las especies de abajo son valores generales de jardinería, NO validados por un especialista.
-- Revisarlos antes de usarlos en reglas de negocio (alertas, índice de vitalidad, etc.).
-- "Bonsai" es una técnica, no una especie: se usa Ficus microcarpa como especie.
CREATE TABLE plantas (
    id                INTEGER GENERATED ALWAYS AS IDENTITY,
    slug              VARCHAR(50)  NOT NULL,
    nombre_comun      VARCHAR(100) NOT NULL,
    nombre_cientifico VARCHAR(150) NOT NULL,
    luz               VARCHAR(20)  NOT NULL,
    riego             VARCHAR(20)  NOT NULL,
    humedad_suelo_min INTEGER      NOT NULL,
    humedad_suelo_max INTEGER      NOT NULL,
    temperatura_min   INTEGER      NOT NULL,
    temperatura_max   INTEGER      NOT NULL,
    luz_lux_min       INTEGER      NOT NULL,
    luz_lux_max       INTEGER      NOT NULL,
    fecha_creacion    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT plantas_pk PRIMARY KEY (id),
    CONSTRAINT plantas_slug_un UNIQUE (slug),
    CONSTRAINT plantas_slug_ck CHECK (slug ~ '^[a-z0-9_]+$'),
    CONSTRAINT plantas_luz_ck CHECK (luz IN ('baja', 'indirecta', 'directa')),
    CONSTRAINT plantas_riego_ck CHECK (riego IN ('bajo', 'moderado', 'alto')),
    CONSTRAINT plantas_humedad_suelo_ck CHECK (
        humedad_suelo_min >= 0
        AND humedad_suelo_max <= 100
        AND humedad_suelo_min < humedad_suelo_max
    ),
    CONSTRAINT plantas_temperatura_ck CHECK (temperatura_min < temperatura_max),
    CONSTRAINT plantas_luz_lux_ck CHECK (
        luz_lux_min >= 0
        AND luz_lux_min < luz_lux_max
    )
);

INSERT INTO plantas (
    slug, nombre_comun, nombre_cientifico, luz, riego,
    humedad_suelo_min, humedad_suelo_max,
    temperatura_min, temperatura_max,
    luz_lux_min, luz_lux_max
) VALUES
    ('monstera',    'Monstera',    'Monstera deliciosa',    'indirecta', 'moderado', 40, 60, 18, 30,  8000, 20000),
    ('calathea',    'Calathea',    'Calathea orbifolia',    'indirecta', 'alto',     60, 80, 18, 27,  3000, 10000),
    ('sansevieria', 'Sansevieria', 'Dracaena trifasciata',  'indirecta', 'bajo',     10, 30, 15, 32,  2000, 15000),
    ('pothos',      'Pothos',      'Epipremnum aureum',     'baja',      'moderado', 30, 50, 15, 30,  1000,  8000),
    ('bonsai',      'Bonsai',      'Ficus microcarpa',      'directa',   'moderado', 40, 60, 15, 28, 10000, 30000);

-- Una planta por matera; nula mientras no se haya elegido.
ALTER TABLE materas ADD COLUMN planta_id INTEGER;
ALTER TABLE materas ADD CONSTRAINT materas_planta_fk
    FOREIGN KEY (planta_id) REFERENCES plantas (id);
