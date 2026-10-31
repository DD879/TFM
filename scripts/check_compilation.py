#!/usr/bin/env python3
"""Compila el corpus con versiones compatibles de solc en Docker y registra los resultados."""
import csv, hashlib, subprocess, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSIONS={"SC09":"0.4.25", "SC12":"0.4.24"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="analysis/compilacion_corpus.csv")
    a=ap.parse_args()
    out=ROOT/a.output
    rows=[]
    for i in range(1,13):
        case=f"SC{i:02d}"; p=ROOT/"contracts"/"blind"/f"{case}.sol"
        ver=VERSIONS.get(case,"0.4.26")
        cmd=["docker","run","--rm","--network","none","--pull","never","-v",f"{p.parent.resolve()}:/src:ro",f"ethereum/solc:{ver}","--bin",f"/src/{p.name}"]
        try:
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
            status="OK" if proc.returncode==0 else "ERROR"
            msg=(proc.stderr or ("Compilación correcta" if status=="OK" else proc.stdout)).strip()[:500]
        except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
            status="NO_EJECUTADO"; msg=str(exc)[:500]
        rows.append([case,ver,hashlib.sha256(p.read_bytes()).hexdigest(),status,msg])
        print(case,ver,status)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f);w.writerow(["id","solc_version","sha256_entrada","compilacion","detalle"]);w.writerows(rows)
    return 0 if all(r[3]=="OK" for r in rows) else 1
if __name__=="__main__":raise SystemExit(main())
