#!/usr/bin/env python3
"""Comprueba los hashes del corpus y, si están disponibles, los originales privados."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = {f'SC{i:02d}' for i in range(1, 13)}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path, key):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows or key not in (reader.fieldnames or []):
        raise ValueError(f'Índice sin datos o sin columna {key}: {path}')
    ids = [row[key] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != EXPECTED_IDS:
        raise ValueError(f'IDs duplicados, ausentes o inesperados en {path}')
    return {row[key]: row for row in rows}


def main():
    errors = []
    try:
        public = load_rows(ROOT / 'public_index.csv', 'contract_id')
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}')
        return 1

    for name in sorted(EXPECTED_IDS):
        entry = public[name]
        filename = f'contracts/blind/{name}.sol'
        path = ROOT / filename
        if entry.get('blind_file') != filename:
            errors.append(f'{name}: ruta pública diferente de {filename}')
        if not path.is_file():
            errors.append(f'{name}: falta {filename}')
            continue
        if digest(path) != entry.get('sha256_blind'):
            errors.append(f'{name}: hash de entrada no coincide con public_index.csv')

    private_file = ROOT / 'ground_truth_private.csv'
    if private_file.is_file():
        try:
            private = load_rows(private_file, 'id')
            from prepare_corpus import remove_comments_keep_lines
            revisions = (ROOT / 'source_revision_private.txt')
            revision = revisions.read_text(encoding='utf-8').strip() if revisions.exists() else None
            for name in sorted(EXPECTED_IDS):
                row = private[name]
                original = ROOT / 'sources_original_private' / name / row['source_file']
                blind = ROOT / 'contracts/blind' / (name + '.sol')
                if not original.is_file() or not blind.is_file():
                    errors.append(f'{name}: falta original o entrada preparada')
                    continue
                if digest(original) != row['sha256_original']:
                    errors.append(f'{name}: hash del original no coincide')
                if digest(blind) != row['sha256_blind']:
                    errors.append(f'{name}: hash privado de la entrada no coincide')
                if row['sha256_blind'] != public[name]['sha256_blind']:
                    errors.append(f'{name}: hash privado distinto del público')
                if row['revision'] != public[name].get('source_revision'):
                    errors.append(f'{name}: revisiones distintas entre índices')
                if revision and revision != row['revision']:
                    errors.append(f'{name}: revisión distinta de source_revision_private.txt')
                source = original.read_text(encoding='utf-8')
                prepared = blind.read_text(encoding='utf-8')
                if remove_comments_keep_lines(source) != prepared:
                    errors.append(f'{name}: la entrada no coincide con el original sin comentarios')
                if '@vulnerable_at_lines' in prepared:
                    errors.append(f'{name}: se ha filtrado una anotación de referencia')
        except (OSError, ValueError, KeyError, UnicodeError) as exc:
            errors.append(f'Comprobación privada: {exc}')
        print('Corpus: verificación pública y privada')
    else:
        print('Corpus: verificación pública (originales privados no disponibles)')

    for name in ('SC01', 'SC04'):
        for tool in ('chatgpt', 'gemini', 'claude'):
            response = ROOT / 'pilot/llms' / tool / (name + '_run01.md')
            if not response.is_file() or not response.stat().st_size:
                errors.append(f'Falta respuesta del piloto: {name}/{tool}')
        for tool, ext in (('slither', 'json'), ('mythril', 'txt')):
            report = ROOT / 'pilot' / tool / f'{name}.{ext}'
            if not report.is_file() or not report.stat().st_size:
                errors.append(f'Falta informe del piloto: {name}/{tool}')
            elif ext == 'json':
                try:
                    document = json.loads(report.read_text(encoding='utf-8'))
                    if document.get('success') is not True:
                        errors.append(f'{name}: Slither no indica éxito')
                except (ValueError, UnicodeError):
                    errors.append(f'{name}: JSON de Slither no válido')

    if errors:
        for error in errors:
            print('ERROR:', error)
        return 1
    print('OK: 12 contratos y evidencias del piloto presentes; hashes coincidentes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
