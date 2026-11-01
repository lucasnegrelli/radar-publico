"""Baixa contratos do PNCP (sem chave) e salva em JSONL.
Uso: python pncp.py 20261001 20261030 [paginas]"""
import json, sys, time, urllib.request, pathlib

BASE = "https://pncp.gov.br/api/consulta/v1/contratos"
ini, fim = sys.argv[1], sys.argv[2]
max_pag = int(sys.argv[3]) if len(sys.argv) > 3 else 5
out = pathlib.Path(__file__).parent.parent / "dados" / f"contratos_{ini}_{fim}.jsonl"

with out.open("w", encoding="utf-8") as f:
    for pag in range(1, max_pag + 1):
        url = f"{BASE}?dataInicial={ini}&dataFinal={fim}&pagina={pag}&tamanhoPagina=50"
        with urllib.request.urlopen(url, timeout=60) as r:
            dados = json.load(r).get("data", [])
        if not dados:
            break
        for d in dados:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
        print(f"pagina {pag}: {len(dados)} contratos")
        time.sleep(0.5)
print("salvo em", out)
