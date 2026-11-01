"""Carrega tudo em dados/radar.duckdb. Rode depois de baixar.py, pncp.py, siconfi.py, camara_api.py."""
import glob, pathlib, duckdb
D = pathlib.Path(__file__).parent.parent / "dados"
con = duckdb.connect(str(D / "radar.duckdb"))
q = lambda s, a=None: con.execute(s, a) if a else con.execute(s)

def tem(p): return bool(glob.glob(str(D / p)))

if tem("contratos_*.jsonl"):
    q(f"CREATE OR REPLACE TABLE pncp_contratos AS SELECT * FROM read_json_auto('{(D/'contratos_*.jsonl').as_posix()}', union_by_name=true, sample_size=-1)")
if tem("siconfi_entes.jsonl"):
    q(f"CREATE OR REPLACE TABLE siconfi_entes AS SELECT * FROM read_json_auto('{(D/'siconfi_entes.jsonl').as_posix()}')")
if tem("camara_deputados.jsonl"):
    q(f"CREATE OR REPLACE TABLE camara_deputados AS SELECT * FROM read_json_auto('{(D/'camara_deputados.jsonl').as_posix()}')")
if tem("csv/Ano-*.csv"):
    q(f"CREATE OR REPLACE TABLE camara_ceap AS SELECT * FROM read_csv('{(D/'csv'/'Ano-*.csv').as_posix()}', delim=';', header=true, all_varchar=true, union_by_name=true, ignore_errors=true)")
if tem("csv/senado_ceaps_*.csv"):
    # o CSV do Senado tem uma linha de metadados antes do cabeçalho: gera cópia limpa
    for f in (D / "csv").glob("senado_ceaps_*.csv"):
        limpo = D / "csv" / f.name.replace("senado_ceaps_", "senado_limpo_")
        txt = f.read_bytes().decode("cp1252", errors="replace").replace(chr(13), "").split(chr(10), 1)[1]
        limpo.write_text(txt, encoding="utf-8", newline=chr(10))
    q("""CREATE OR REPLACE TABLE senado_ceaps AS SELECT * FROM read_csv(?, delim=';', quote='"', escape='"', header=true, all_varchar=true, union_by_name=true, strict_mode=false)""", [(D / "csv" / "senado_limpo_*.csv").as_posix()])
if tem("csv/receitas_candidatos_*.csv"):
    q(f"CREATE OR REPLACE TABLE tse_receitas AS SELECT * FROM read_csv('{(D/'csv'/'receitas_candidatos_*.csv').as_posix()}', delim=';', header=true, all_varchar=true, encoding='latin-1', union_by_name=true, ignore_errors=true)")

if tem("csv/consulta_cand_*_BRASIL.csv"):
    q(f"CREATE OR REPLACE TABLE tse_cand AS SELECT * FROM read_csv('{(D/'csv'/'consulta_cand_*_BRASIL.csv').as_posix()}', delim=';', header=true, all_varchar=true, encoding='latin-1', strict_mode=false)")
for nome in ("ceis", "cnep"):
    if tem(f"csv/*_{nome.upper()}.csv"):
        q(f"CREATE OR REPLACE TABLE {nome} AS SELECT * FROM read_csv(?, delim=';', header=true, all_varchar=true, encoding='latin-1', strict_mode=false)",
          [(D / "csv" / f"*_{nome.upper()}.csv").as_posix()])

for (t,) in q("SHOW TABLES").fetchall():
    print(f"{t:20s}", q(f"SELECT count(*) FROM {t}").fetchone()[0], "linhas")