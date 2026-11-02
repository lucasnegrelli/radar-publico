"""TSE histórico (2018, 2020, 2022): candidaturas, bens declarados, receitas e despesas de campanha -> dados/csv e dados/tse/*.parquet
Uso: python tse_historico.py 2022 2018 ... Idempotente."""
import sys, zipfile, urllib.request, pathlib, duckdb
RAIZ = pathlib.Path(__file__).parent.parent / "dados"
BR, CSV, PQ = RAIZ / "bruto", RAIZ / "csv", RAIZ / "tse"
for d in (BR, CSV, PQ): d.mkdir(parents=True, exist_ok=True)
B = "https://cdn.tse.jus.br/estatistica/sead/odsele/"
def baixar(rel, dest):
    if dest.exists(): return
    print("baixando", rel, flush=True); urllib.request.urlretrieve(B + rel, dest)
for arg in sys.argv[1:]:
    ano, _, so = arg.partition(":"); so = set(so.split(",")) if so else None
    fontes = [("consulta_cand", f"consulta_cand/consulta_cand_{ano}.zip", f"consulta_cand_{ano}_BRASIL.csv"),
              ("bens", f"bem_candidato/bem_candidato_{ano}.zip", f"bem_candidato_{ano}_BRASIL.csv"),
              ("receitas", f"prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{ano}.zip", f"receitas_candidatos_{ano}_BRASIL.csv"),
              ("despesas", f"prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{ano}.zip", f"despesas_pagas_candidatos_{ano}_BRASIL.csv"),
              ("fornec", f"prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{ano}.zip", f"despesas_contratadas_candidatos_{ano}_BRASIL.csv")]
    for tipo, rel, arq in fontes:
        if so and tipo not in so: continue
        alvo = PQ / f"{tipo}_{ano}.parquet"
        if alvo.exists(): continue
        z = BR / pathlib.Path(rel).name; baixar(rel, z)
        with zipfile.ZipFile(z) as zf:
            if arq not in zf.namelist(): print("ausente no zip:", arq, [n for n in zf.namelist() if tipo[:5] in n][:5]); continue
            zf.extract(arq, CSV)
        src = (CSV / arq).as_posix(); feito = False
        for enc in ("utf-8", "latin-1"):
            try:
                duckdb.sql(f"COPY (select * from read_csv('{src}', delim=';', header=true, encoding='{enc}', all_varchar=true, quote='\"', sample_size=-1)) TO '{alvo.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"); feito = True; break
            except Exception as e: print("encoding", enc, "falhou:", str(e)[:100].replace(chr(10), " "))
        if not feito:  # arquivo misto: decodifica na marra
            tmp = CSV / ("_u8_" + arq); tmp.write_bytes((CSV / arq).read_bytes().decode("cp1252", errors="replace").encode("utf-8"))
            duckdb.sql(f"COPY (select * from read_csv('{tmp.as_posix()}', delim=';', header=true, all_varchar=true, quote='\"', sample_size=-1)) TO '{alvo.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"); tmp.unlink()
        (CSV / arq).unlink()
        print("ok", alvo.name, duckdb.sql(f"select count(*) from '{alvo.as_posix()}'").fetchall()[0][0], flush=True)
