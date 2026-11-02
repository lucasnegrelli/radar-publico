"""Lista as janelas (quinzenas) de PNCP que ainda NÃO estão no Hugging Face.
Uso: python pncp_pendentes.py 2026-08 2026-10   -> imprime  janelas=["2026-10-01_2026-10-15", ...]"""
import sys, os, json, calendar, datetime
from huggingface_hub import HfApi

REPO = os.environ.get("HF_REPO", "propagang/radar-publico-dados")
PREFIXO = os.environ.get("PREFIXO", "pncp")
api = HfApi(token=os.environ.get("HF_TOKEN"))
try:
    existentes = {f for f in api.list_repo_files(REPO, repo_type="dataset") if f.startswith(PREFIXO + "/")}
except Exception:
    existentes = set()

def meses(ini, fim):
    a, m = map(int, ini.split("-")); b, n = map(int, fim.split("-"))
    while (a, m) <= (b, n):
        yield a, m
        m += 1
        if m == 13: a, m = a + 1, 1

pendentes = []
for a, m in reversed(list(meses(sys.argv[1], sys.argv[2]))):
    u = calendar.monthrange(a, m)[1]
    for de, ate in ((1, 15), (16, u)):
        j = f"{a}-{m:02d}-{de:02d}_{a}-{m:02d}-{ate:02d}"
        recente = datetime.date.fromisoformat(f"{a}-{m:02d}-{ate:02d}") >= datetime.date.today() - datetime.timedelta(days=21)
        # janelas recentes são sempre refeitas (ainda recebem contratos novos e retificações)
        if recente and datetime.date.fromisoformat(f"{a}-{m:02d}-{de:02d}") <= datetime.date.today() or f"{PREFIXO}/{j}.parquet" not in existentes:
            pendentes.append(j)
print("janelas=" + json.dumps(pendentes))
