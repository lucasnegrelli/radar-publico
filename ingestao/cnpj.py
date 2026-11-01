"""Baixa o dump de CNPJ (espelho casadosdados da base da Receita) e converte para Parquet enxuto.
Uso: python cnpj.py [AAAA-MM-DD]. Saída: dados/cnpj/{empresas,estabelecimentos,socios}_N.parquet.
Apaga zip/csv de cada parte depois de converter (economiza disco). Idempotente."""
import sys, pathlib, subprocess, zipfile, duckdb

DATA = sys.argv[1] if len(sys.argv) > 1 else "2026-10-13"
BASE = f"https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/{DATA}/"
RAIZ = pathlib.Path(__file__).parent.parent / "dados"
TMP, OUT = RAIZ / "tmp_cnpj", RAIZ / "cnpj"
TMP.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)

OPC = "delim=';', quote='\"', escape='\"', header=false, all_varchar=true, encoding='latin-1', strict_mode=false"
def cols(*n): return "{" + ",".join(f"'{c}':'VARCHAR'" for c in n) + "}"

SQL = {
 "Socios": (cols("cnpj_basico","tipo_socio","nome_socio","doc_socio","qualificacao","data_entrada","pais","doc_rep","nome_rep","qualif_rep","faixa_etaria"),
            "SELECT cnpj_basico, tipo_socio, nome_socio, doc_socio, qualificacao, data_entrada, nome_rep"),
 "Empresas": (cols("cnpj_basico","razao_social","natureza","qualif_resp","capital_social","porte","ente_fed"),
              "SELECT cnpj_basico, razao_social, natureza, try_cast(replace(capital_social,',','.') AS DOUBLE) AS capital_social, porte"),
 "Estabelecimentos": (cols("cnpj_basico","cnpj_ordem","cnpj_dv","matriz","fantasia","situacao","data_situacao","motivo","cidade_ext","pais",
                           "data_inicio","cnae","cnae_sec","tp_logr","logr","numero","compl","bairro","cep","uf","municipio","ddd1","tel1","ddd2","tel2","ddd_fax","fax","email","sit_esp","data_sit_esp"),
                      "SELECT cnpj_basico || cnpj_ordem || cnpj_dv AS cnpj, cnpj_basico, matriz, fantasia, situacao, data_situacao, data_inicio, cnae, uf, municipio, cep"),
}

for tipo, n in [("Socios", 10), ("Empresas", 10), ("Estabelecimentos", 10)]:
    colunas, sel = SQL[tipo]
    for i in range(n):
        alvo = OUT / f"{tipo.lower()}_{i}.parquet"
        if alvo.exists(): continue
        z = TMP / f"{tipo}{i}.zip"
        print("baixando", z.name, flush=True)
        if not z.exists() or z.stat().st_size < 1000:
            subprocess.run(["curl", "-sS", "--fail", "-m", "3600", "-o", str(z), BASE + z.name], check=True)
        with zipfile.ZipFile(z) as zf:
            nome = zf.namelist()[0]; zf.extract(nome, TMP)
        csv = TMP / nome
        duckdb.sql(f"COPY ({sel} FROM read_csv('{csv.as_posix()}', {OPC}, columns={colunas})) TO '{alvo.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        csv.unlink(); z.unlink()
        print("ok", alvo.name, flush=True)
print("FIM", flush=True)
