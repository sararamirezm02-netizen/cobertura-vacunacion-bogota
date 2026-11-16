"""Crea cobertura.db (SQLite) a partir del CSV de SaluData."""
import csv, os, re, sqlite3

CSV = "osb-seguimiento-vacunacion-sectores.csv"
DB = "cobertura.db"
INST = {"ICBF": "ICBF", "COLEGIOS PRIVADOS": "Colegios privados", "COLEGIOS OFICIALES": "Colegios oficiales",
        "INTEGRACIÓN": "SDIS (Integración Social)", "INTERACIÓN VEJÉZ": "SDIS Vejez"}
DESCARTAR = {"21 - Localidad Desconocida", "NO ACTUALIZADO"}

def limpio(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s[0].upper() + s[1:]

if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
con.executescript(open("schema.sql", encoding="utf-8").read())
ids = {"localidad": {}, "biologico": {}, "institucion": {}}

def obtener(tabla, nombre):
    d = ids[tabla]
    if nombre not in d:
        d[nombre] = len(d) + 1
        con.execute(f"INSERT INTO {tabla} (id, nombre) VALUES (?, ?)", (d[nombre], nombre))
    return d[nombre]

cargadas = 0
with open(CSV, encoding="latin-1", newline="") as f:
    filas = [r for r in csv.DictReader(f, delimiter=";") if r["NOMBRE_LOCALIDAD"] not in DESCARTAR]
# Las localidades se registran en orden (01 Usaquén ... 20 Sumapaz)
for nombre in sorted({r["NOMBRE_LOCALIDAD"] for r in filas}):
    obtener("localidad", re.sub(r"^\d+ - ", "", nombre))
for r in filas:
    loc = obtener("localidad", re.sub(r"^\d+ - ", "", r["NOMBRE_LOCALIDAD"]))
    bio = obtener("biologico", limpio(r["BIOLOGICO_EDAD"]))
    ins = obtener("institucion", INST[r["INSTITUCION"]])
    con.execute("""INSERT INTO cobertura (fecha_reporte, localidad_id, biologico_id, institucion_id,
                   dosis_aplicada, denominador) VALUES (?,?,?,?,?,?)""",
                (r["FECHA_REPORTE"], loc, bio, ins, int(r["DOSIS_APLICADA"]), int(r["DENOMINADOR"])))
    cargadas += 1
con.commit()
con.close()
print(f"Base creada: {DB} ({cargadas} registros cargados)")
