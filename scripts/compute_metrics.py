#!/usr/bin/env python3
"""Calcula TP/FP/FN, precision, recall y F1 a partir de adjudicaciones revisadas."""
import csv,sys,collections
from pathlib import Path

def ratio(a,b):return round(a/b,4) if b else None

def main(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    counts=collections.defaultdict(lambda:collections.Counter())
    seen=set()
    for r in rows:
        outcome=(r.get('outcome') or '').strip().upper()
        if outcome not in {'TP','FP','FN','PENDING'}:
            raise SystemExit('Valor outcome inválido: '+repr(outcome))
        if outcome=='PENDING':continue
        key=(r.get('contract_id',''),r.get('tool',''),r.get('model',''),r.get('run_id',''),r.get('finding_id',''))
        if key in seen:raise SystemExit('Hallazgo duplicado: '+repr(key))
        seen.add(key)
        grp=(r.get('tool',''),r.get('model',''),r.get('category',''))
        counts[grp][outcome]+=1
    print('tool,model,category,TP,FP,FN,precision,recall,F1')
    for (tool,model,cat),c in sorted(counts.items()):
        tp,fp,fn=c['TP'],c['FP'],c['FN']
        precision=ratio(tp,tp+fp);recall=ratio(tp,tp+fn)
        f1=round(2*precision*recall/(precision+recall),4) if precision is not None and recall is not None and (precision+recall)>0 else None
        print(','.join(map(str,[tool,model,cat,tp,fp,fn,precision if precision is not None else '',recall if recall is not None else '',f1 if f1 is not None else ''])))

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Uso: python3 scripts/compute_metrics.py analysis/adjudicaciones.csv')
    main(sys.argv[1])
