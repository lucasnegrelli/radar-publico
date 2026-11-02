"""Atualiza no banco as fontes que mudam todo dia, para rodar no GitHub Actions (nada na máquina do usuário):
CEIS/CNEP (Portal da Transparência), cota da Câmara (CEAP) e do Senado (CEAPS). Depois recarrega as tabelas (carregar.py)
e exporta ceis/cnep em Parquet para dados/tse/ (usado pelas emendas e pelas fichas de pessoa)."""
import sys, io, zipfile, datetime, pathlib, urllib.request, urllib.error, subprocess
RAIZ = pathlib.Path(__file__).parent.parent
import duckdb
# o banco foi salvo numa máquina Windows: as views emp/estab apontam para caminhos absolutos de lá. São recriadas pelo exportador com caminhos relativos.
_c = duckdb.connect(str(RAIZ / "dados" / "radar.duckdb"))
for _v in ("emp", "estab"): _c.execute(f"DROP VIEW IF EXISTS {_v}")
_c.close()
CSV = RAIZ / "dados" / "csv"; BR = RAIZ / "dados" / "bruto"
CSV.mkdir(parents=True, exist_ok=True); BR.mkdir(parents=True, exist_ok=True)
def get(url, dest):
    urllib.request.urlretrieve(url, dest)

# CEIS / CNEP: o arquivo é datado; tenta de hoje para trás
for nome in ("ceis", "cnep", "cepim"):
    for d in range(0, 25 if nome == "cepim" else 10):
        dia = (datetime.date.today() - datetime.timedelta(days=d)).strftime("%Y%m%d")
        try:
            z = BR / f"{nome}_{dia}.zip"
            get(f"https://portaldatransparencia.gov.br/download-de-dados/{nome}/{dia}", z)
            if z.stat().st_size < 1000: continue
            for velho in CSV.glob(f"*_{nome.upper()}.csv"): velho.unlink()
            zipfile.ZipFile(z).extractall(CSV)
            print("ok", nome, dia, flush=True); break
        except Exception as e:
            continue
    else:
        print("AVISO: não achei", nome, "recente; mantém o do banco", flush=True)

# cota parlamentar: o carregar.py recria a tabela só com os anos presentes, então baixa todos os anos de 2023 em diante
for ano in range(2023, datetime.date.today().year + 1):
    try:
        z = BR / f"ceap_{ano}.zip"; get(f"https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip", z)
        zipfile.ZipFile(z).extract(f"Ano-{ano}.csv", CSV)
        get(f"https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv", CSV / f"senado_ceaps_{ano}.csv")
        print("ok cota", ano, flush=True)
    except Exception as e:
        print("AVISO cota", ano, e, flush=True); sys.exit(1)   # sem todos os anos, recarregar apagaria dados

subprocess.run([sys.executable, str(RAIZ / "ingestao" / "carregar.py")], check=True)
import duckdb
c = duckdb.connect(str(RAIZ / "dados" / "radar.duckdb"))
(RAIZ / "dados" / "tse").mkdir(exist_ok=True)
for t in ("ceis", "cnep"):
    c.execute(f"copy {t} to '{(RAIZ / 'dados' / 'tse' / (t + '.parquet')).as_posix()}' (format parquet, compression zstd)")
print("fontes atualizadas")
