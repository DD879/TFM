# Corpus Solidity

Los archivos `blind/SC01.sol` a `blind/SC12.sol` proceden de SmartBugs Curated. Se han eliminado los comentarios y conservado el código y sus saltos de línea. La revisión de origen, las rutas y los hashes SHA-256 están recogidos en `../public_index.csv`.

Los originales anotados y las etiquetas están en `../sources_original_private/` y `../ground_truth_private.csv` (no se publican en Git). Los nombres de contratos y funciones se mantienen, por lo que la eliminación de comentarios no oculta todas las pistas sobre el fallo.

Comprobar el corpus desde la raíz:

```bash
python3 scripts/check_repo_integrity.py
```

Preparar una entrada numerada para el protocolo V4:

```bash
python3 scripts/prepare_prompt_v4.py contracts/blind/SC01.sol
```

Los hashes prueban la identidad de los archivos, no que todos los contratos compilen ni que sus anotaciones sean exhaustivas. Evitar cambios en las entradas una vez iniciada la campaña; una variante nueva necesita su propio hash y registro.
