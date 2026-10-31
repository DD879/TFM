# Análisis de resultados

Archivos de trabajo para registrar ejecuciones, adjudicar hallazgos y evaluar las explicaciones:

| Archivo | Uso |
| --- | --- |
| `registro_ejecuciones_v4.csv` | Fecha, modelo, configuración y rutas de cada ejecución. |
| `adjudicaciones.csv` | Clasificación que lee `scripts/compute_metrics.py` (`TP`, `FP`, `FN`, `PENDING`). |
| `adjudicacion_v4.csv` | Ficha detallada por hallazgo para la revisión manual. |
| `rubrica.csv` | Puntuación 0–2 de localización, explicación, severidad y mitigación. |

`adjudicacion_v4.csv` y `adjudicaciones.csv` tienen esquemas distintos. El script de métricas utiliza el segundo; las clasificaciones de la ficha detallada deben trasladarse a ese esquema después de revisarlas.

Registrar un `FN` para cada vulnerabilidad de referencia no detectada en una ejecución. Agrupar alertas duplicadas de una misma causa raíz y mantener como `PENDING` los hallazgos que todavía no se hayan podido confirmar o descartar. El cálculo deja las tasas en blanco si hay hallazgos pendientes en el grupo. Cerrar las adjudicaciones antes de comparar herramientas.
