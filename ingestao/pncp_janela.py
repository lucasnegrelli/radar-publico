"""Baixa os contratos do PNCP de UMA janela de datas -> dados/pncp/DE_ATE.parquet
Uso: python pncp_janela.py 2026-10-01_2026-10-15
Respeita o limite do servidor: poucos trabalhadores, pausa entre requisições e espera longa em 429."""
import sys, json, time, pathlib, urllib.request, urllib.error, tempfile
from concurrent.futures import ThreadPoolExecutor
import duckdb

JANELA = sys.argv[1]
DE, ATE = JANELA.split("_")
RAIZ = pathlib.Path(__file__).parent.parent / "dados" / "pncp"
RAIZ.mkdir(parents=True, exist_ok=True)
ALVO = RAIZ / f"{JANELA}.parquet"
BASE = "https://pncp.gov.br/api/consulta/v1/contratos"
TRABALHADORES = 2

def pegar(url, tentativas=10):
    for t in range(tentativas):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"accept": "application/json"}), timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 204: return {"data": [], "totalPaginas": 0}
            time.sleep(40 * (t + 1) if e.code == 429 else 3 * (t + 1))
        except Exception:
            time.sleep(3 * (t + 1))
    return None

SELECT = """select numeroControlePNCP id, numeroControlePncpCompra compra, orgaoEntidade.cnpj orgao_cnpj, orgaoEntidade.razaoSocial orgao,
  orgaoEntidade.esferaId esfera, orgaoEntidade.poderId poder, unidadeOrgao.ufSigla uf, unidadeOrgao.municipioNome municipio, unidadeOrgao.codigoIbge ibge,
  tipoPessoa tipo_pessoa, niFornecedor fornecedor_doc, nomeRazaoSocialFornecedor fornecedor, tipoContrato.nome tipo_contrato, categoriaProcesso.nome categoria,
  objetoContrato objeto, valorInicial valor_inicial, valorGlobal valor_global, valorAcumulado valor_acumulado,
  dataAssinatura data_assinatura, dataVigenciaInicio vigencia_ini, dataVigenciaFim vigencia_fim, emendaParlamentar emenda, frutoAdesao adesao, processo"""

q = f"dataInicial={DE.replace('-', '')}&dataFinal={ATE.replace('-', '')}&tamanhoPagina=500"
p1 = pegar(f"{BASE}?{q}&pagina=1")
if not p1:
    raise SystemExit("falhou a primeira página")
total = p1.get("totalPaginas", 1)
print(f"{JANELA}: {p1.get('totalRegistros')} contratos em {total} páginas", flush=True)
tmp = pathlib.Path(tempfile.mkdtemp(prefix="pncp_")) / "j.jsonl"
falhas = []
with tmp.open("w", encoding="utf-8") as f, ThreadPoolExecutor(TRABALHADORES) as ex:
    for d in p1["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    feitas = 1
    for pg, r in zip(range(2, total + 1), ex.map(lambda p: pegar(f"{BASE}?{q}&pagina={p}"), range(2, total + 1))):
        if r is None: falhas.append(pg); continue
        for d in r["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n")
        feitas += 1
        if feitas % 25 == 0: print(f"  {feitas}/{total} páginas", flush=True)
if falhas:
    raise SystemExit(f"{len(falhas)} páginas falharam, não vou salvar janela incompleta: {falhas[:10]}")
duckdb.sql(f"COPY ({SELECT} from read_json_auto('{tmp.as_posix()}', union_by_name=true, sample_size=-1, maximum_object_size=33554432)) TO '{ALVO.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
print("ok", ALVO.name, flush=True)
