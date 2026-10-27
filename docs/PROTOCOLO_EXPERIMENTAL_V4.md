# Protocolo experimental V4 (PEC 2)

La versión V3 corresponde exclusivamente al piloto de SC01 y SC04. **No mezclar las ejecuciones V3 con la campaña V4** al calcular métricas.

## Alcance
- Comparación principal: ChatGPT GPT-6 Instant; Gemini 3.1 Pro (razonamiento Medio); Claude Sonnet 5.5 (esfuerzo Medio). Los tres sistemas se evaluarán mediante interfaces conversacionales.
- Las tres herramientas se evaluarán en modo conversacional, sin acceso a Internet, repositorios externos ni ejecución de comandos. Se registrarán modelo, configuración, fecha y respuesta íntegra.
- Corpus: 12 contratos blind SC01–SC12, con ground truth privado separado.
- Tres ejecuciones independientes por contrato y herramienta en la campaña principal (108 auditorías previstas); una sesión nueva por ejecución, sin memoria del proyecto ni acceso a la referencia de verdad.

## Preparar entrada numerada
Desde la raíz de `~/TFM`, tras copiar `prompts/auditoria_v4.txt` y `scripts/prepare_prompt_v4.py`:

```bash
python3 scripts/prepare_prompt_v4.py contracts/blind/SC01.sol
```

El script genera `pilot/inputs_v4/SC01_v4_prompt.txt` y `pilot/inputs_v4/SC01_v4_metadata.json`. El archivo `.sol` permanece intacto. Los prefijos `L001 |` se utilizan únicamente para localizar instrucciones. Las tres herramientas recibirán exactamente el mismo prompt numerado.

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
No se compartirá el ground truth con los modelos. Las pruebas se realizarán en sesiones independientes, sin búsqueda web ni archivos adicionales. La posible contaminación del benchmark se documentará como amenaza a la validez.

## Estado
V4 está **definida y lista para una validación de formato**, pero no se presenta como ejecutada. Los resultados V3 del piloto se conservan sin modificar.
