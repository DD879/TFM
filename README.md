# TFM — Auditoría de seguridad de smart contracts con IA generativa

Trabajo Final del Máster en Ciberseguridad y Privacidad (UOC). El proyecto compara ChatGPT, Gemini y Claude con Slither y Mythril en la detección de vulnerabilidades de contratos Solidity. La memoria del TFM es un documento único que se amplía durante el semestre.

## Estado del proyecto

- **Corpus:** 12 contratos de SmartBugs Curated, distribuidos en cinco categorías. Los archivos de entrada están en `contracts/blind/` y se han preparado eliminando comentarios sin modificar el resto del código.
- **Piloto V3:** SC01 y SC04 analizados con los tres modelos conversacionales, Slither y Mythril. Las respuestas y los informes están en `pilot/`.
- **Campaña V4:** protocolo y prompt preparados. Se prevén tres sesiones por contrato y plataforma (108 auditorías conversacionales). Todavía no hay resultados de esa campaña.

El corpus procede de un benchmark público y puede ser conocido por los modelos. Sus etiquetas se utilizan como referencia inicial y los hallazgos adicionales deben revisarse antes de clasificarlos.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `contracts/blind/` | Doce contratos de entrada, SC01–SC12. |
| `public_index.csv` | Procedencia, revisión de SmartBugs y hash de cada entrada. |
| `prompts/` | V3 (piloto) y V4 (campaña principal). |
| `pilot/` | Entradas de trabajo y evidencias originales de SC01 y SC04. |
| `docs/PROTOCOLO_EXPERIMENTAL_V4.md` | Procedimiento de ejecución y clasificación de hallazgos. |
| `docs/versions.csv` | Versiones y configuraciones a registrar. |
| `analysis/` | Plantillas de ejecuciones, adjudicación y valoración de mitigaciones. |
| `results/` | Destino de los resultados de la campaña principal. |
| `docker/mythril/` | Imagen adaptada para descargar compiladores antiguos. |
| `scripts/` | Preparación del corpus y prompts, verificación y cálculo de métricas. |
| `literature/` | Matriz de estudios y referencias utilizadas en el estado del arte. |

Los originales y sus anotaciones están en `sources_original_private/`, `manifest_private.json` y `ground_truth_private.csv` y se mantienen fuera de Git. Tampoco deben suministrarse a los modelos durante las pruebas.

## Uso

Ejecutar desde la raíz del proyecto:

```bash
python3 scripts/check_repo_integrity.py
python3 scripts/prepare_prompt_v4.py contracts/blind/SC01.sol
```

El verificador comprueba los hashes públicos; si encuentra los originales y etiquetas privados, comprueba también su correspondencia. Para regenerar el corpus desde la revisión fijada de SmartBugs se necesita `manifest_private.json`:

```bash
python3 scripts/prepare_corpus.py --download
```

La descarga no sobrescribe contratos existentes salvo que se indique `--overwrite`. En ese caso se deben revisar de nuevo los hashes antes de usar los resultados anteriores.

Una vez completada y revisada la clasificación de los hallazgos:

```bash
python3 scripts/compute_metrics.py analysis/adjudicaciones.csv
```

Las métricas requieren tanto detecciones correctas como falsos negativos registrados explícitamente. Las ejecuciones del piloto V3 no se combinan con las de V4.
