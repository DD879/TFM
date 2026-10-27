#!/usr/bin/env python3
"""Fetch exact upstream SmartBugs files and create comment-blinded audit copies.

Run from repository root: python3 scripts/prepare_corpus.py
No third-party Python packages are required. Requires network access to GitHub.
"""
import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'manifest_private.json').read_text(encoding='utf-8'))
BASE = 'https://raw.githubusercontent.com/smartbugs/smartbugs-curated/'
ORIG = ROOT / 'sources_original_private'
BLIND = ROOT / 'contracts' / 'blind'
ORIG.mkdir(parents=True, exist_ok=True)
BLIND.mkdir(parents=True, exist_ok=True)


def remove_comments_keep_lines(src):
    """Replace comment characters with spaces, preserving newlines and strings."""
    out = []
    i, n = 0, len(src)
    state, quote = 'code', ''
    while i < n:
        c = src[i]
        nxt = src[i+1] if i+1 < n else ''
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
        else:  # string literal
            out.append(c)
            if c == '\\' and i+1 < n:
                out.append(src[i+1]); i += 2; continue
            if c == quote:
                state = 'code'
        i += 1
    return ''.join(out)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'TFM-PEC2-academic-research/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8-sig')


def resolve_commit():
    try:
        api = 'https://api.github.com/repos/smartbugs/smartbugs-curated/commits/main'
        commit = json.loads(fetch(api))['sha']
        if not re.fullmatch('[0-9a-f]{40}', commit):
            raise ValueError('Unexpected commit SHA')
        return commit
    except Exception as exc:
        print('WARN: could not pin upstream commit:', exc)
        return 'main'


def main():
    revision = resolve_commit()
    rows = []
    for c in MANIFEST['contracts']:
        url = BASE + revision + '/' + c['path']
        src = fetch(url)
        if '@vulnerable_at_lines' not in src or 'pragma solidity' not in src:
            raise ValueError('Unexpected upstream source content: ' + c['id'])
        clean = remove_comments_keep_lines(src)
        if clean.count('\n') != src.count('\n'):
            raise ValueError('Line count changed: ' + c['id'])
        if '<yes>' in clean or '@vulnerable_at_lines' in clean:
            raise ValueError('Annotation leakage in ' + c['id'])
        (ORIG / c['id']).mkdir(exist_ok=True)
        (ORIG / c['id'] / c['file']).write_text(src, encoding='utf-8')
        (BLIND / (c['id'] + '.sol')).write_text(clean, encoding='utf-8')
        rows.append({
            'id': c['id'], 'source_file': c['file'], 'upstream_path': c['path'],
            'upstream_url': url, 'revision': revision,
            'sha256_original': hashlib.sha256(src.encode('utf-8')).hexdigest(),
            'sha256_blind': hashlib.sha256(clean.encode('utf-8')).hexdigest(),
            'pragma_reference': c['pragma_reference'],
            'category': c['category'], 'swc': c['swc'] or '',
            'reported_lines_original': ';'.join(map(str,c['reported_lines'])),
            'location_reviewed': 'NO', 'compilation_checked': 'NO',
            'notes': 'Source annotations are provisional, verify function/line manually'
        })
        print('OK', c['id'], c['file'], '=> contracts/blind/'+c['id']+'.sol')
    output = ROOT / 'ground_truth_private.csv'
    with output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    (ROOT / 'source_revision_private.txt').write_text(revision+'\n', encoding='utf-8')
    print('\nGenerated', len(rows), 'blind Solidity files.')
    print('Private ground truth:', output)
    print('IMPORTANT: do not expose ground_truth_private.csv or sources_original_private/ to LLMs.')
    print('Next: compile and inspect each file. The original annotation line numbers may be imprecise.')


if __name__ == '__main__':
    main()
