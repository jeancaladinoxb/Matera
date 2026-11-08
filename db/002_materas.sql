-- Requiere db/001_usuarios.sql (clave foránea a usuarios.id).
CREATE TABLE materas (
    id                INTEGER GENERATED ALWAYS AS IDENTITY,
    mac               VARCHAR(12) NOT NULL,
    usuario_id        INTEGER,
    estado            VARCHAR(20) NOT NULL DEFAULT 'sin_reclamar',
    fecha_vinculacion TIMESTAMPTZ,
    fecha_creacion    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT materas_pk PRIMARY KEY (id),
    CONSTRAINT materas_mac_un UNIQUE (mac),
    CONSTRAINT materas_usuario_fk FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    CONSTRAINT materas_mac_ck CHECK (mac ~ '^[0-9A-F]{12}$'),
    CONSTRAINT materas_estado_ck CHECK (estado IN ('sin_reclamar', 'vinculada')),
    CONSTRAINT materas_estado_coherente_ck CHECK (
        (estado = 'sin_reclamar' AND usuario_id IS NULL AND fecha_vinculacion IS NULL)
        OR (estado = 'vinculada' AND usuario_id IS NOT NULL AND fecha_vinculacion IS NOT NULL)
    )
);
