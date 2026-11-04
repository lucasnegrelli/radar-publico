"""Banco Central IF.data: Resumo (ativo, captações, patrimônio líquido...) de todas as instituições por trimestre.
Saída: dados/bcb/ifdata_resumo.parquet e dados/bcb/ifdata_cadastro.parquet"""
import json, time, pathlib, urllib.request, urllib.parse, duckdb

RAIZ = pathlib.Path(__file__).parent.parent / "dados" / "bcb"
RAIZ.mkdir(parents=True, exist_ok=True)
B = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"

def get(url, tent=5):
    for t in range(tent):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            time.sleep(4 * (t + 1))
    return None

def trimestres(ini=2022, fim=2026):
    for a in range(ini, fim + 1):
        for m in ("03", "06", "09", "12"):
            yield f"{a}{m}"

linhas, cad = [], []
for am in trimestres():
    url = f"{B}/IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)?@AnoMes={am}&@TipoInstituicao=1&@Relatorio='1'&$format=json&$top=100000"
    d = get(url)
    v = (d or {}).get("value", [])
    if not v: print(am, "sem dados"); continue
    linhas += [{"AnoMes": x["AnoMes"], "CodInst": x["CodInst"], "Coluna": x["NomeColuna"], "Saldo": x["Saldo"]} for x in v if x["NomeColuna"] in
               ("Ativo Total", "Captações", "Patrimônio Líquido", "Carteira de Crédito Classificada", "Lucro Líquido", "Passivo Circulante e Exigível a Longo Prazo e Resultados de Exercícios Futuros")]
    c = get(f"{B}/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes={am}&$format=json&$top=100000")
    cad += (c or {}).get("value", [])
    print(am, len(v), "valores |", len(cad), "cadastros acumulados", flush=True)
    time.sleep(1)

pq = RAIZ / "ifdata_resumo.parquet"; cq = RAIZ / "ifdata_cadastro.parquet"
tmp = RAIZ / "_tmp.json"; tmp.write_text(json.dumps(linhas), encoding="utf-8")
duckdb.sql(f"COPY (SELECT * FROM read_json_auto('{tmp.as_posix()}')) TO '{pq.as_posix()}' (FORMAT PARQUET)")
if cad:
    tmp.write_text(json.dumps(cad), encoding="utf-8")
    duckdb.sql(f"COPY (SELECT * FROM read_json_auto('{tmp.as_posix()}', sample_size=-1)) TO '{cq.as_posix()}' (FORMAT PARQUET)")
else:
    print("cadastro veio vazio (API instável): mantendo o cadastro anterior")
tmp.unlink()
print("ok", len(linhas), "linhas de resumo,", len(cad), "linhas de cadastro")
