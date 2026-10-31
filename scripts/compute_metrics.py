#!/usr/bin/env python3
"""Calcula métricas a partir de un CSV de adjudicaciones completadas."""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = {'contract_id', 'tool', 'model', 'run_id', 'finding_id', 'category', 'outcome'}
OUTCOMES = {'TP', 'FP', 'FN', 'PENDING'}


def fraction(numerator, denominator):
    return numerator / denominator if denominator else None


def main(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED.difference(reader.fieldnames or [])
        if missing:
            raise ValueError('Faltan columnas: ' + ', '.join(sorted(missing)))
        rows = list(reader)
    if not rows:
        raise ValueError('No hay adjudicaciones; no se pueden calcular métricas')

    counts = defaultdict(Counter)
    seen = set()
    pending = Counter()
    for number, row in enumerate(rows, start=2):
        for key in REQUIRED:
            if not (row.get(key) or '').strip():
                raise ValueError(f'Fila {number}: campo vacío {key}')
        outcome = row['outcome'].strip().upper()
        if outcome not in OUTCOMES:
            raise ValueError(f'Fila {number}: outcome no válido ({outcome})')
        key = tuple(row[column].strip() for column in ('contract_id','tool','model','run_id','finding_id'))
        if key in seen:
            raise ValueError(f'Fila {number}: hallazgo duplicado {key}')
        seen.add(key)
        group = tuple(row[column].strip() for column in ('tool','model','category'))
        if outcome == 'PENDING':
            pending[group] += 1
        else:
            counts[group][outcome] += 1

    print('tool,model,category,TP,FP,FN,PENDING,precision,recall,F1')
    for group in sorted(set(counts) | set(pending)):
        values = counts[group]
        tp, fp, fn = values['TP'], values['FP'], values['FN']
        precision = fraction(tp, tp + fp)
        recall = fraction(tp, tp + fn)
        f1 = (fraction(2 * precision * recall, precision + recall) if precision + recall else 0.0) if precision is not None and recall is not None else None
        if pending[group]:
            precision = recall = f1 = None  # Esperar a cerrar la adjudicación.
        fmt = lambda value: '' if value is None else f'{value:.4f}'
        print(','.join((*group, str(tp),str(fp),str(fn),str(pending[group]), fmt(precision),fmt(recall),fmt(f1))))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python3 scripts/compute_metrics.py analysis/adjudicaciones.csv')
    try:
        main(sys.argv[1])
    except (ValueError, OSError) as exc:
        raise SystemExit(f'ERROR: {exc}')
