# Protocolo experimental V4 (PEC 2)

La versión V3 corresponde exclusivamente al piloto de SC01 y SC04. **No mezclar las ejecuciones V3 con la campaña V4** al calcular métricas.

## Alcance
- Comparación principal: ChatGPT GPT-6 Instant; Gemini 3.1 Pro, razonamiento Medio; Claude Code (modelo y versión exactos pendientes de registrar en la ejecución). Registrar los nombres que muestre cada herramienta, pues los proveedores pueden cambiarlos.
- Claude Code es un agente y no equivale a Claude web. Las respuestas de Claude web del piloto V3 no cuentan como pruebas de Claude Code. La campaña V4 de Claude Code requiere permisos restringidos, registro de herramientas y acciones ejecutadas; las diferencias de modalidad deben discutirse en el análisis.
- Corpus: 12 contratos blind SC01–SC12, con ground truth privado separado.
- Tres ejecuciones independientes por contrato y herramienta en la campaña principal (108 auditorías previstas); una sesión nueva por ejecución, sin memoria del proyecto ni acceso a la referencia de verdad.

## Preparar entrada numerada
Desde la raíz de `~/TFM`, tras copiar `prompts/auditoria_v4.txt` y `scripts/prepare_prompt_v4.py`:

```bash
python3 scripts/prepare_prompt_v4.py contracts/blind/SC01.sol
```

El script genera `pilot/inputs_v4/SC01_v4_prompt.txt` y `pilot/inputs_v4/SC01_v4_metadata.json`. El archivo `.sol` permanece intacto. Los prefijos `L001 |` son una vista de lectura y no deben copiarse a los analizadores o al compilador. ChatGPT y Gemini reciben la vista numerada. Claude Code puede recibirla como instrucción junto al acceso de solo lectura al mismo `.sol`; si utiliza herramientas, se registrarán todos los permisos y comandos, y esa diferencia de modalidad se reconocerá explícitamente.

## Registro mínimo por ejecución
Contrato, fuente SHA-256, plataforma, nombre exacto del modelo, modalidad, esfuerzo/razonamiento, fecha y hora, prompt V4, archivo de entrada, respuesta original, herramientas disponibles y eventuales rechazos. Conservar la respuesta completa sin corregirla.

## Adjudicación
- **TP**: hallazgo real del ground truth identificado con categoría y ubicación verificables.
- **FN**: vulnerabilidad real etiquetada no detectada.
- **FP**: hallazgo de seguridad descartado tras revisión independiente; no basta que esté ausente del benchmark.
- **Duplicado**: dos alertas de una misma causa raíz; contar una sola.
- **Informativo**: observación de estilo, gas, mantenimiento o calidad sin vulnerabilidad sustentada; no contar automáticamente como FP.
- **Pendiente**: hallazgo adicional no adjudicado; excluir temporalmente de métricas hasta revisarlo.

La localización se considera exacta cuando el modelo identifica la instrucción o línea afectada inequívocamente. El número Lxxx es ayuda de trazabilidad, no requisito exclusivo.

## Calidad de explicaciones y parches
Cuatro dimensiones, 0–2 puntos cada una: localización, explicación, severidad, mitigación. Un parche meramente plausible y sin verificar no puede recibir 2/2 en mitigación. Para 2/2: compilar con la versión adecuada y probar localmente la corrección sin regresiones relevantes. Compilar no prueba ausencia de otras vulnerabilidades.

## Repetibilidad
Registrar por separado (a) frecuencia de detección por vulnerabilidad en tres ejecuciones y (b) estabilidad entre conjuntos de hallazgos normalizados de las repeticiones. No confundir frecuencia de detección con consistencia global.

## Seguridad metodológica
No compartir ground truth con los modelos. Un prompt que prohíbe herramientas no garantiza aislamiento; Claude Code necesita controles reales de permisos, ficheros y red. SmartBugs es público y puede estar contaminado en entrenamiento; anonimizar identificadores no elimina esa amenaza.

## Estado
V4 está **definida y lista para una validación de formato**, pero no se presenta como ejecutada. Los resultados V3 del piloto se conservan sin modificar.
