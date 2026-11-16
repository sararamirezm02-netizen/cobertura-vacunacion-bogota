"""Servidor sencillo: sirve la app y consulta la base de datos SQLite. Solo usa la biblioteca estándar."""
import json, sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DB = "cobertura.db"

def consultar(sql, params=()):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(f) for f in con.execute(sql, params)]
    finally:
        con.close()

def nivel(pct):
    return consultar("SELECT codigo, etiqueta, recomendacion FROM reglas_semaforo "
                     "WHERE ? >= min_pct ORDER BY min_pct DESC LIMIT 1", (pct,))[0]

def opciones():
    return {"localidades": consultar("SELECT id, nombre FROM localidad ORDER BY id"),
            "biologicos": consultar("SELECT id, nombre FROM biologico ORDER BY nombre"),
            "instituciones": consultar("SELECT id, nombre FROM institucion ORDER BY id")}

FILTRO_INST = "AND (? = 0 OR institucion_id = ?)"

def cobertura(loc, bio, ins):
    f = consultar(f"""SELECT SUM(dosis_aplicada) AS dosis, SUM(denominador) AS denominador
                      FROM cobertura WHERE localidad_id = ? AND biologico_id = ? {FILTRO_INST}""",
                  (loc, bio, ins, ins))[0]
    if not f["denominador"]:
        return {"sin_datos": True}
    pct = f["dosis"] / f["denominador"] * 100
    return {"dosis": f["dosis"], "denominador": f["denominador"], "pct": pct, "meta": 95, **nivel(pct)}

def ranking(bio, ins):
    filas = consultar(f"""SELECT l.id, l.nombre, SUM(c.dosis_aplicada) AS dosis, SUM(c.denominador) AS denominador
                          FROM cobertura c JOIN localidad l ON l.id = c.localidad_id
                          WHERE c.biologico_id = ? {FILTRO_INST.replace('institucion_id', 'c.institucion_id')}
                          GROUP BY l.id HAVING SUM(c.denominador) > 0""", (bio, ins, ins))
    for f in filas:
        f["pct"] = f["dosis"] / f["denominador"] * 100
        f["codigo"] = nivel(f["pct"])["codigo"]
    return sorted(filas, key=lambda f: -f["pct"])

class Manejador(BaseHTTPRequestHandler):
    def responder(self, cuerpo, tipo="application/json; charset=utf-8", codigo=200):
        datos = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        url = urlparse(self.path)
        try:
            q = {k: int(v[0]) for k, v in parse_qs(url.query).items()}
            if url.path == "/":
                self.responder(open("index.html", "rb").read(), "text/html; charset=utf-8")
            elif url.path == "/api/opciones":
                self.responder(opciones())
            elif url.path == "/api/cobertura":
                self.responder(cobertura(q["localidad"], q["biologico"], q.get("institucion", 0)))
            elif url.path == "/api/ranking":
                self.responder(ranking(q["biologico"], q.get("institucion", 0)))
            else:
                self.responder({"error": "No encontrado"}, codigo=404)
        except (KeyError, ValueError):
            self.responder({"error": "Parámetros inválidos"}, codigo=400)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print("App disponible en http://localhost:8000  (Ctrl+C para detener)")
    HTTPServer(("localhost", 8000), Manejador).serve_forever()
