#!/usr/bin/env python3
"""Prepara una entrada de auditoría V4 reproducible sin modificar el Solidity original."""
from pathlib import Path
import argparse, hashlib, json

parser=argparse.ArgumentParser()
parser.add_argument('contract',type=Path,help='Ruta al contrato blind SCxx.sol')
parser.add_argument('--prompt',type=Path,default=Path('prompts/auditoria_v4.txt'))
parser.add_argument('--output-dir',type=Path,default=Path('pilot/inputs_v4'))
args=parser.parse_args()
raw=args.contract.read_bytes()
code=raw.decode('utf-8')
base=args.prompt.read_text(encoding='utf-8')
if base.count('[CODIGO_NUMERADO]') != 1:
    raise SystemExit('ERROR: falta el marcador [CODIGO_NUMERADO] o está repetido')
lines=code.splitlines()
width=max(3,len(str(len(lines))))
numbered='\n'.join(f'L{i:0{width}d} | {line}' for i,line in enumerate(lines,1))
message=base.replace('[CODIGO_NUMERADO]',numbered)
args.output_dir.mkdir(parents=True,exist_ok=True)
stem=args.contract.stem
out=args.output_dir/(stem+'_v4_prompt.txt')
out.write_text(message+'\n',encoding='utf-8')
meta={
 'contract_id':stem,
 'source_file':str(args.contract),
 'source_sha256':hashlib.sha256(raw).hexdigest(),
 'source_line_count':len(lines),
 'prompt_version':'v4',
 'prompt_sha256':hashlib.sha256(args.prompt.read_bytes()).hexdigest(),
 'prepared_input':str(out),
 'notes':'Vista numerada; no modifica ni recompila el fichero .sol original.'
}
metaout=args.output_dir/(stem+'_v4_metadata.json')
metaout.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
print(metaout)
