CREATE TABLE usuarios (
    id             INTEGER GENERATED ALWAYS AS IDENTITY,
    nombre         VARCHAR(100) NOT NULL,
    apellido       VARCHAR(100) NOT NULL,
    nickname       VARCHAR(100) NOT NULL,
    correo         VARCHAR(254) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT usuarios_pk PRIMARY KEY (id),
    CONSTRAINT usuarios_correo_un UNIQUE (correo)
);
