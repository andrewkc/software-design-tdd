CREATE TABLE IF NOT EXISTS bodegas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cuentas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    rol TEXT NOT NULL CHECK (rol IN ('administrador', 'jefe', 'empleado')),
    activo BOOLEAN NOT NULL DEFAULT true,
    bodega_id TEXT REFERENCES bodegas(id),
    CONSTRAINT administrador_sin_bodega CHECK (rol <> 'administrador' OR bodega_id IS NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS una_jefatura_por_bodega
    ON cuentas (bodega_id)
    WHERE rol = 'jefe' AND bodega_id IS NOT NULL;
