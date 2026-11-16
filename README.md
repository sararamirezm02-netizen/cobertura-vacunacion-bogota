# Cobertura de vacunación por localidad en Bogotá

Prototipo académico de **Habilidades Investigativas I** (Ingeniería de Software, Universidad de La Salle). Es una app que permite elegir una localidad de Bogotá y una vacuna para ver la cobertura de vacunación, su distancia frente a la meta nacional del 95 % y un semáforo con una recomendación.

## ¿Cómo funciona?

1. Los datos se cargan en una base de datos relacional (tablas `localidad`, `biologico`, `institucion`, `cobertura` y `reglas_semaforo`).
2. La app filtra la localidad y la vacuna elegidas y calcula la cobertura: dosis aplicadas ÷ población objetivo × 100.
3. Aplica el semáforo de SaluData: **verde** (95 % o más), **amarillo** (90 % a 94 %) y **rojo** (menos de 90 %).
4. Muestra el resultado, la brecha frente a la meta y un ranking de las 20 localidades.

## Dos versiones

| Carpeta | Descripción |
|---|---|
| `docs/` | Versión web que corre en el navegador con SQL (AlaSQL). Se publica con GitHub Pages. |
| `app/` | Versión con servidor en Python y base de datos SQLite real. |

### Ejecutar la versión con SQLite

Requisito: Python 3 (sin librerías adicionales).

```bash
cd app
python crear_bd.py     # opcional: vuelve a crear cobertura.db desde el CSV
python servidor.py
```

Luego abre http://localhost:8000. En Windows, si `python` no funciona, usa `py`.

## Datos

- **Fuente:** Secretaría Distrital de Salud de Bogotá, SaluData, tablero "Seguimiento cobertura vacunación sectores": https://saludata.saludcapital.gov.co/osb/indicadores/cobertura-vacunacion-sectores/
- **Corte de los datos:** 26 de agosto de 2025.
- **Columnas del CSV:** `FECHA_REPORTE`, `NOMBRE_LOCALIDAD`, `BIOLOGICO_EDAD`, `INSTITUCION`, `DOSIS_APLICADA`, `DENOMINADOR` y `COBERTURA` (esta última viene por mil).
- Se descartan los registros con localidad desconocida o no actualizada.

## Limitaciones

Son datos de seguimiento por sector (ICBF, colegios, SDIS) y no la cobertura anual oficial del Programa Ampliado de Inmunizaciones, y el corte corresponde a 2025.

## Origen del umbral del 95 % y de los cortes del semáforo:
el umbral del 95 % no es una cifra definida por el grupo, sino una referencia que aparece en tres fuentes: el tablero de seguimiento de vacunación de SaluData, que clasifica la cobertura como satisfactoria cuando alcanza el 95 % o más, como insatisfactoria entre el 90 % y el 94 % y como crítica por debajo de ese rango; el Plan de Intensificación de la Vacunación 2026 del Ministerio de Salud y Protección Social, que fija como meta alcanzar coberturas iguales o superiores al 95 % con los biológicos del Programa Ampliado de Inmunizaciones; y las estimaciones de cobertura de la OMS y UNICEF (WUENIC), que señalan ese nivel como el necesario para prevenir brotes de enfermedades inmunoprevenibles. Por esa razón la aplicación usa el 95 % como meta nacional de comparación y adopta los mismos cortes del semáforo de la plataforma, de modo que el resultado que ve el usuario coincide con la clasificación oficial de la fuente de los datos.
