"""Sócios estrangeiros de empresas brasileiras (Receita/CNPJ) -> dados/cnpj/socios_ext_N.parquet
Guarda só sócios com país diferente de Brasil. Apaga o bruto depois de converter."""
import sys, pathlib, subprocess, zipfile, duckdb
DATA = sys.argv[1] if len(sys.argv) > 1 else "2026-10-13"
BASE = f"https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/{DATA}/"
RAIZ = pathlib.Path(__file__).parent.parent / "dados"
TMP, OUT = RAIZ / "tmp_cnpj", RAIZ / "cnpj"; TMP.mkdir(parents=True, exist_ok=True)
COLS = "{" + ",".join(f"'{c}':'VARCHAR'" for c in ["cnpj_basico","tipo_socio","nome_socio","doc_socio","qualificacao","data_entrada","pais","doc_rep","nome_rep","qualif_rep","faixa_etaria"]) + "}"
for i in range(10):
    alvo = OUT / f"socios_ext_{i}.parquet"
    if alvo.exists(): continue
    z = TMP / f"SociosExt{i}.zip"
    subprocess.run(["curl", "-sS", "--fail", "-m", "3600", "-o", str(z), BASE + f"Socios{i}.zip"], check=True)
    with zipfile.ZipFile(z) as zf:
        nome = zf.namelist()[0]; zf.extract(nome, TMP)
    csv = TMP / nome
    duckdb.sql(f"""COPY (SELECT cnpj_basico, tipo_socio, nome_socio, qualificacao, data_entrada, pais FROM read_csv('{csv.as_posix()}', delim=';', quote='"', escape='"', header=false,
        all_varchar=true, encoding='latin-1', strict_mode=false, columns={COLS}) WHERE pais IS NOT NULL AND pais NOT IN ('', '105')) TO '{alvo.as_posix()}' (FORMAT PARQUET)""")
    csv.unlink(); z.unlink(); print("ok", alvo.name, flush=True)
print("FIM", flush=True)
