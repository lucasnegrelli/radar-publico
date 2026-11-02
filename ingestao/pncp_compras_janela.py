"""Baixa as LICITAÇÕES (compras) do PNCP de uma janela de datas, com modalidade e valores -> dados/compras/DE_ATE.parquet
Serve para conferir o valor de cada contrato contra o valor da compra de origem e saber como foi contratado.
Uso: python pncp_compras_janela.py 2026-10-01_2026-10-15"""
import sys, json, time, pathlib, urllib.request, urllib.error, tempfile
from concurrent.futures import ThreadPoolExecutor
import duckdb

JANELA = sys.argv[1]
DE, ATE = JANELA.split("_")
RAIZ = pathlib.Path(__file__).parent.parent / "dados" / "compras"
RAIZ.mkdir(parents=True, exist_ok=True)
ALVO = RAIZ / f"{JANELA}.parquet"
BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
TRABALHADORES = 2
TAM = 50

def pegar(url, tentativas=10):
    for t in range(tentativas):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"accept": "application/json"}), timeout=90) as r:
                corpo = r.read().decode("utf-8")
                return json.loads(corpo) if corpo.strip() else {"data": [], "totalPaginas": 0}
        except urllib.error.HTTPError as e:
            if e.code == 204: return {"data": [], "totalPaginas": 0}
            if e.code == 400: return {"data": [], "totalPaginas": 0, "_erro": 400}
            time.sleep(40 * (t + 1) if e.code == 429 else 3 * (t + 1))
        except Exception:
            time.sleep(3 * (t + 1))
    return None

tmp = pathlib.Path(tempfile.mkdtemp(prefix="compras_")) / "c.jsonl"
n_tot, falhas = 0, []
with tmp.open("w", encoding="utf-8") as f, ThreadPoolExecutor(TRABALHADORES) as ex:
    for mod in range(1, 15):
        q = f"dataInicial={DE.replace('-', '')}&dataFinal={ATE.replace('-', '')}&codigoModalidadeContratacao={mod}&tamanhoPagina={TAM}"
        p1 = pegar(f"{BASE}?{q}&pagina=1")
        if p1 is None: falhas.append((mod, 1)); continue
        if not p1.get("data"): continue
        total = p1.get("totalPaginas", 1)
        print(f"modalidade {mod}: {p1.get('totalRegistros')} compras em {total} páginas", flush=True)
        for d in p1["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n"); n_tot += 1
        for pg, r in zip(range(2, total + 1), ex.map(lambda p: pegar(f"{BASE}?{q}&pagina={p}"), range(2, total + 1))):
            if r is None: falhas.append((mod, pg)); continue
            for d in r["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n"); n_tot += 1
if falhas:
    raise SystemExit(f"{len(falhas)} páginas falharam; não salvo janela incompleta: {falhas[:8]}")
if n_tot == 0:
    duckdb.sql(f"COPY (SELECT NULL::VARCHAR id) TO '{ALVO.as_posix()}' (FORMAT PARQUET)"); print("janela vazia"); raise SystemExit(0)
duckdb.sql(f"""COPY (select numeroControlePNCP id, orgaoEntidade.cnpj orgao_cnpj, anoCompra ano, sequencialCompra seq, modalidadeId modalidade_id, modalidadeNome modalidade,
   modoDisputaNome modo_disputa, amparoLegal.nome amparo, srp, situacaoCompraNome situacao, valorTotalEstimado valor_estimado, valorTotalHomologado valor_homologado,
   dataPublicacaoPncp publicado, objetoCompra objeto
   from read_json_auto('{tmp.as_posix()}', union_by_name=true, sample_size=-1, maximum_object_size=33554432)) TO '{ALVO.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)""")
print("ok", ALVO.name, n_tot, "compras", flush=True)
