# Prueba piloto — V3

Los casos SC01 y SC04 se utilizaron para comprobar el procedimiento antes de iniciar la campaña V4.

| Herramienta | Evidencias |
| --- | --- |
| ChatGPT | `llms/chatgpt/SC01_run01.md`, `SC04_run01.md` |
| Gemini | `llms/gemini/SC01_run01.md`, `SC04_run01.md` |
| Claude | `llms/claude/SC01_run01.md`, `SC04_run01.md` |
| Slither | `slither/SC01.json`, `SC04.json` |
| Mythril | `mythril/SC01.txt`, `SC04.txt` |

En ambos casos las tres respuestas conversacionales identificaron el tipo de vulnerabilidad principal: reentrancia (SC01) y autorización con `tx.origin` (SC04). También aparecen alertas adicionales que requieren adjudicación técnica; las mitigaciones propuestas no se han sometido a pruebas de regresión.

`inputs_v4/` contiene una entrada preparada de SC01 para la siguiente fase, no un resultado de V4. `workspace_aislado/` conserva material de trabajo local. Ambos directorios están excluidos de Git.

Conservar los informes originales sin edición. Al ejecutar nuevas pruebas, registrar junto a cada salida el hash del archivo analizado, las versiones de las herramientas y el comando completo. No sumar resultados del piloto V3 a las métricas de V4.
