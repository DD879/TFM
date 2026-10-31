#!/usr/bin/env python3
"""Verifica offline o (explicitamente) reconstruye el corpus desde revision fijada.

Por defecto no realiza descargas ni escrituras:
    python3 scripts/prepare_corpus.py --verify
Para reconstruir, con Internet y revision fijada:
    python3 scripts/prepare_corpus.py --download
Para sobrescribir el corpus existente (solo si es imprescindible):
    python3 scripts/prepare_corpus.py --download --overwrite
"""
import argparse
import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/smartbugs/smartbugs-curated/'


def remove_comments_keep_lines(src):
    """Sustituye comentarios por espacios conservando saltos y literales."""
    out, i, n = [], 0, len(src)
    state, quote = 'code', ''
    while i < n:
        c, nxt = src[i], src[i+1] if i+1 < n else ''
        if state == 'code':
            if c == '/' and nxt == '/':
                out.extend('  '); i += 2; state = 'line'; continue
            if c == '/' and nxt == '*':
                out.extend('  '); i += 2; state = 'block'; continue
            if c in ('"', "'"):
                state = 'string'; quote = c
            out.append(c)
        elif state == 'line':
            if c == '\n':
                out.append(c); state = 'code'
            else:
                out.append(' ')
        elif state == 'block':
            if c == '*' and nxt == '/':
                out.extend('  '); i += 2; state = 'code'; continue
            out.append(c if c == '\n' else ' ')
        else:
            out.append(c)
            if c == '\\' and i+1 < n:
                out.append(src[i+1]); i += 2; continue
            if c == quote:
                state = 'code'
        i += 1
    if state == 'block':
        raise ValueError('Comentario de bloque sin cerrar')
    return ''.join(out)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'TFM-PEC2-academic-research/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8-sig')


def write_corpus(revision, overwrite):
    if not re.fullmatch(r'[a-f0-9]{40}', revision):
        raise ValueError('Se requiere SHA completo de commit upstream (no main ni master).')
    manifest_file = ROOT / 'manifest_private.json'
    if not manifest_file.exists():
        raise FileNotFoundError('Falta manifest_private.json (privado); no se puede reconstruir corpus')
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    originals, blind = ROOT / 'sources_original_private', ROOT / 'contracts/blind'
    target = [originals / c['id'] / c['file'] for c in manifest['contracts']]
    target += [blind / (c['id'] + '.sol') for c in manifest['contracts']]
    target += [ROOT/'ground_truth_private.csv', ROOT/'source_revision_private.txt']
    existing = [p for p in target if p.exists()]
    if existing and not overwrite:
        raise FileExistsError(f'Hay {len(existing)} ficheros existentes. Se prohíbe sobrescribirlos sin --overwrite.')
    # Descargar y comprobar todas las fuentes antes de escribir cualquiera
    staged, rows = [], []
    for c in manifest['contracts']:
        if not re.fullmatch(r'SC\d{2}', c['id']) or '/' in c['file']:
            raise ValueError('ID o nombre de origen inseguro: ' + c['id'])
        url = BASE + revision + '/' + c['path']
        src = fetch(url)
        if '@vulnerable_at_lines' not in src or 'pragma solidity' not in src:
            raise ValueError('Contenido de benchmark inesperado: ' + c['id'])
        cleaned = remove_comments_keep_lines(src)
        if cleaned.count('\n') != src.count('\n') or '@vulnerable_at_lines' in cleaned:
            raise ValueError('Filtracion de etiqueta o cambio de lineas: ' + c['id'])
        staged.append((c, src, cleaned))
        rows.append({
            'id': c['id'], 'source_file': c['file'], 'upstream_path': c['path'],
            'upstream_url': url, 'revision': revision,
            'sha256_original': hashlib.sha256(src.encode('utf-8')).hexdigest(),
            'sha256_blind': hashlib.sha256(cleaned.encode('utf-8')).hexdigest(),
            'pragma_reference': c['pragma_reference'], 'category': c['category'],
            'swc': c['swc'] or '', 'reported_lines_original': ';'.join(map(str,c['reported_lines'])),
            'location_reviewed': 'NO', 'compilation_checked': 'NO',
            'notes': 'Anotaciones iniciales del benchmark; requieren verificacion manual'
        })
    for c, src, cleaned in staged:
        orig_path = originals / c['id'] / c['file']
        orig_path.parent.mkdir(parents=True, exist_ok=True)
        blind.mkdir(parents=True, exist_ok=True)
        orig_path.write_text(src, encoding='utf-8')
        (blind / (c['id']+'.sol')).write_text(cleaned, encoding='utf-8')
    with (ROOT / 'ground_truth_private.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    (ROOT / 'source_revision_private.txt').write_text(revision+'\n', encoding='utf-8')
    # Actualizar indice publico atomizado para que los hashes correspondan al nuevo corpus.
    with (ROOT/'public_index.csv').open('w',newline='',encoding='utf-8') as f:
        cols = ['contract_id','blind_file','status','source_revision','upstream_path','sha256_blind','pilot_v3_report_available']
        w = csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow({'contract_id':r['id'],'blind_file':'contracts/blind/'+r['id']+'.sol',
                        'status':'prepared_comments_removed_unverified_compilation',
                        'source_revision':revision,'upstream_path':r['upstream_path'],
                        'sha256_blind':r['sha256_blind'],
                        'pilot_v3_report_available':'yes' if all((ROOT/'pilot'/'llms'/name/(r['id']+'_run01.md')).is_file() for name in ('chatgpt','gemini','claude')) else 'no'})
    print(f'ATENCION: se ha regenerado el corpus ({len(rows)} contratos). Los informes del piloto previo NO demuestran correspondencia con esta revision. Revalidar antes de comparar.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--verify',action='store_true',help='Modo offline/no destructivo (por defecto)')
    group.add_argument('--download',action='store_true',help='Descarga explicitamente fuentes desde la revision fijada')
    parser.add_argument('--overwrite',action='store_true',help='Permite reemplazar archivos existentes al usar --download')
    parser.add_argument('--revision',default=None,help='Commit SHA de 40 caracteres (por defecto source_revision_private.txt)')
    args=parser.parse_args()
    if not args.download:
        if args.overwrite or args.revision:
            parser.error('--overwrite y --revision se usan solamente con --download')
        from check_repo_integrity import main as verify
        return verify()
    src = ROOT / 'source_revision_private.txt'
    revision = args.revision or (src.read_text(encoding='utf-8').strip() if src.exists() else None)
    if not revision:
        parser.error('No se conoce la revision fijada. Aportar --revision <SHA del commit>.')
    write_corpus(revision,args.overwrite)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
