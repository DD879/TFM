# TFM: evaluación de IA generativa para auditar smart contracts

Repositorio de trabajo para el TFM del Máster en Ciberseguridad y Privacidad (UOC).

**Estado:** estructura preparada; no se han añadido contratos, pruebas ni resultados. No confundir la preparación del repositorio con la ejecución del experimento.

## Objetivo y alcance
- Corpus principal: 10-15 contratos Solidity; objetivo operativo: 12.
- Categorías previstas: reentrancia, control de acceso, llamadas no comprobadas, errores aritméticos y denegación de servicio.
- Sistemas evaluados: ChatGPT, Gemini, Claude Code; baselines: Slither y Mythril (si son compatibles).
- Experimento principal: tres ejecuciones independientes por contrato y plataforma de IA, según coste y disponibilidad.
- Experimento secundario: dos variantes de modelo sobre 4-6 contratos (opcional).

## Estructura
- `contracts/original/`: contratos fuente con atribución y licencia.
- `contracts/clean/`: versiones sin comentarios que revelen vulnerabilidades.
- `contracts/controls/`: controles negativos o variantes revisadas.
- `ground_truth/metadata.csv`: etiquetas verificadas (separadas de las entradas de los modelos).
- `prompts/auditoria_v1.txt`: instrucciones comunes.
- `results/llms/` y `results/baseline/`: resultados literales, sin edición.
- `analysis/adjudicaciones.csv`: clasificación manual revisada.
- `analysis/rubrica.csv`: evaluación cualitativa.
- `scripts/compute_metrics.py`: cálculo reproducible de métricas.
- `literature/`: búsquedas y matriz de fuentes.
- `pilot/`: evidencias de la prueba piloto.

## Inicio rápido
1. Crear un repositorio GitHub vacío y subir estos archivos (sin secretos ni claves).
2. Buscar contratos de SmartBugs Curated y verificar licencia, vulnerabilidad y versión de Solidity.
3. Rellenar `ground_truth/metadata.csv` con 10-15 contratos **reales**, sin datos inventados.
4. Crear versiones limpias y comprobar que mantienen la vulnerabilidad.
5. Instalar Slither y, si es posible, Mythril en un entorno aislado; registrar versiones.
6. Ejecutar piloto con dos contratos y registrar las salidas y metadatos.
7. Revisar criterios de clasificación antes de la campaña principal.

Para calcular métricas tras adjudicar hallazgos:
`python3 scripts/compute_metrics.py analysis/adjudicaciones.csv`

**Nota metodológica:** un hallazgo ausente del ground truth no es automáticamente un falso positivo. Debe revisarse y adjudicarse.
