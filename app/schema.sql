-- Modelo relacional de la app de cobertura de vacunación (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE localidad   (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE);
CREATE TABLE biologico   (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE);
CREATE TABLE institucion (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE);

CREATE TABLE cobertura (
  id             INTEGER PRIMARY KEY,
  fecha_reporte  TEXT    NOT NULL,
  localidad_id   INTEGER NOT NULL REFERENCES localidad(id),
  biologico_id   INTEGER NOT NULL REFERENCES biologico(id),
  institucion_id INTEGER NOT NULL REFERENCES institucion(id),
  dosis_aplicada INTEGER NOT NULL CHECK (dosis_aplicada >= 0),
  denominador    INTEGER NOT NULL CHECK (denominador >= 0)
);
CREATE INDEX idx_cobertura_consulta ON cobertura (biologico_id, localidad_id, institucion_id);

-- Reglas del semáforo (clasificación del tablero de SaluData)
CREATE TABLE reglas_semaforo (
  codigo         TEXT PRIMARY KEY,      -- verde / amarillo / rojo
  etiqueta       TEXT NOT NULL,
  min_pct        REAL NOT NULL,         -- cobertura mínima para este nivel
  recomendacion  TEXT NOT NULL
);
INSERT INTO reglas_semaforo VALUES
 ('verde',   'Satisfactoria',   95, 'La cobertura cumple la meta. Mantén al día el esquema de vacunación de tu familia.'),
 ('amarillo','Insatisfactoria', 90, 'Está cerca de la meta. Revisa el carné y completa las dosis pendientes.'),
 ('rojo',    'Crítica',          0, 'Está lejos de la meta. Acude a tu punto de vacunación para completar el esquema.');
