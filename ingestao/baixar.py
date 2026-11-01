"""Baixa os arquivos em massa (CEAP Câmara, CEAPS Senado, TSE) em dados/bruto e extrai em dados/csv.
Idempotente: pula o que já existe. Uso: python baixar.py [ano_ceap ...] ; TSE_ANO por env (padrão 2024)."""
import os, sys, urllib.request, zipfile, pathlib

RAIZ = pathlib.Path(__file__).parent.parent / "dados"
BRUTO, CSV = RAIZ / "bruto", RAIZ / "csv"
BRUTO.mkdir(parents=True, exist_ok=True); CSV.mkdir(parents=True, exist_ok=True)

def baixar(url, destino):
    if destino.exists():
        print("já existe:", destino.name); return
    print("baixando", url)
    urllib.request.urlretrieve(url, destino)

anos = sys.argv[1:] or ["2025"]
for ano in anos:
    z = BRUTO / f"ceap_{ano}.zip"
    baixar(f"https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip", z)
    if not (CSV / f"Ano-{ano}.csv").exists():
        zipfile.ZipFile(z).extract(f"Ano-{ano}.csv", CSV)
    baixar(f"https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv",
           CSV / f"senado_ceaps_{ano}.csv")

tse = os.environ.get("TSE_ANO", "2024")
z = BRUTO / f"tse_cand_{tse}.zip"
baixar(f"https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{tse}.zip", z)
with zipfile.ZipFile(z) as zf:
    for n in zf.namelist():
        if n.startswith(f"receitas_candidatos_{tse}_") and "BRASIL" not in n and not (CSV / n).exists():
            zf.extract(n, CSV)
print("ok")
