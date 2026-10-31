# Protocolo experimental V4

## 1. Diseño

Se compararán ChatGPT (GPT-6 Instant), Gemini (3.1 Pro, razonamiento Medio) y Claude (Sonnet 5.5, esfuerzo Medio) mediante sus interfaces conversacionales. Las denominaciones exactas y ajustes se registrarán en cada ejecución; los niveles de razonamiento no se consideran equivalentes entre proveedores.

El corpus principal consta de doce contratos Solidity (`contracts/blind/SC01.sol`–`SC12.sol`) procedentes de SmartBugs Curated. La campaña comprende tres ejecuciones independientes por contrato y plataforma: **108 auditorías conversacionales**. Slither y Mythril son las dos líneas base. Los resultados del piloto V3 (SC01 y SC04) se conservarán aparte.

## 2. Preparación de entradas

Desde la raíz del proyecto:

```bash
python3 scripts/check_repo_integrity.py
python3 scripts/prepare_prompt_v4.py contracts/blind/SC01.sol
```

El generador inserta el Solidity en `prompts/auditoria_v4.txt`, con numeración `L001`, `L002`, etc. La misma entrada se facilitará a los tres modelos. Se archivarán el texto exacto enviado y los hashes del código, la plantilla y la entrada preparada.

No adjuntar a las conversaciones `ground_truth_private.csv`, `manifest_private.json`, fuentes anotadas, resultados del piloto ni `public_index.csv`.

## 3. Ejecución

Cada repetición se hará en una conversación nueva y sin contexto de otras pruebas. Desactivar o aislar memorias, instrucciones personales, documentos y herramientas con capacidad de consultar datos externos. Si alguna condición no puede comprobarse, se anotará en la ficha de ejecución.

Registrar: ID del contrato, plataforma, modelo y versión mostrados, modo de razonamiento, fecha y zona horaria, hashes, versión del prompt, funciones habilitadas, respuesta completa y cualquier rechazo. No reformular la petición a partir de la respuesta de otra herramienta ni orientar al modelo hacia una categoría concreta. Los parámetros no mostrados por la interfaz se dejarán sin valor.

## 4. Unidad de evaluación y adjudicación

La unidad será una vulnerabilidad independiente dentro de cada contrato, identificada por causa raíz, categoría y localización. Cuando varias alertas describan el mismo fallo, se registrarán sus referencias originales y se contabilizará un único hallazgo.

| Clasificación | Criterio |
| --- | --- |
| `TP` | Vulnerabilidad real detectada con causa y localización suficientes. |
| `FN` | Vulnerabilidad de referencia que la ejecución no ha identificado. |
| `FP` | Alerta descartada tras revisión técnica de su viabilidad. |
| `PENDING` | Hallazgo adicional que aún necesita comprobación. |
| Informativo | Observación de estilo, gas o mantenimiento que no implica un fallo demostrado. |

La ausencia de una alerta en el benchmark no basta para clasificarla como FP. Los casos pendientes se mantendrán separados de los recuentos definitivos. Registrar explícitamente un FN por cada vulnerabilidad de referencia que no se detecte; no inferir los FN de la ausencia de filas en un CSV. El número de línea solo es una ayuda: también se comprobarán función e instrucción afectadas.

Las adjudicaciones para el cálculo se registrarán en `analysis/adjudicaciones.csv`. La rúbrica se cumplimentará en `analysis/rubrica.csv`. Las decisiones dudosas se revisarán por segunda vez y quedarán acompañadas de su justificación.

## 5. Métricas y consistencia

Se calcularán los recuentos `TP`, `FP` y `FN` y, cuando sus denominadores no sean cero, precisión, recall y F1. Los resultados se presentarán por plataforma y categoría, con los recuentos absolutos. No se utilizarán las ejecuciones V3 para estimar el rendimiento de V4.

La frecuencia de detección de cada vulnerabilidad será el número de repeticiones correctas entre tres. La consistencia se medirá por separado comparando los conjuntos de hallazgos normalizados de cada pareja de ejecuciones mediante Jaccard (`|A ∩ B| / |A ∪ B|`). Para dos conjuntos vacíos se fijará el acuerdo en 1 y se señalará expresamente. Se mostrarán los tres pares y su media descriptiva para cada contrato.

Las alertas pendientes y los controles negativos ausentes limitan la interpretación de los falsos positivos. No se generalizará el resultado de doce contratos a todos los contratos Solidity.

## 6. Explicaciones y propuestas de corrección

La evaluación cualitativa puntuará de 0 a 2 la localización, la explicación causal, la justificación de la severidad y la mitigación. Un parche plausible no alcanzará la puntuación máxima sin compilar y superar una prueba local que compruebe la corrección del fallo conocido. La compilación aislada no demuestra seguridad.

## 7. Amenazas a la validez

Los contratos de SmartBugs son públicos y pueden formar parte de los datos de entrenamiento de los modelos. Se han eliminado comentarios, pero se conservan nombres originales y otras pistas. El procedimiento no permite descartar contaminación ni afirmar que las etiquetas públicas describan todas las vulnerabilidades posibles.

Si se ensayan variantes con identificadores neutralizados o controles negativos, se documentarán como condiciones separadas con sus propios hashes y comprobaciones de compilación. No se mezclarán con la serie principal. Todos los análisis se realizarán sobre código público y en entornos autorizados, sin pruebas contra contratos desplegados de terceros.
