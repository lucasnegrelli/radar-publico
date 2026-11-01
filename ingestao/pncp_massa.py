"""Baixa TODOS os contratos do PNCP por mês (paralelo, retomável) -> dados/pncp/AAAA-MM.parquet
Uso: python pncp_massa.py 2025-01 2026-10   (mês inicial e final, inclusive)"""
import sys, json, time, calendar, pathlib, urllib.request, urllib.error, tempfile
from concurrent.futures import ThreadPoolExecutor
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent / "dados" / "pncp"
RAIZ.mkdir(parents=True, exist_ok=True)
BASE = "https://pncp.gov.br/api/consulta/v1/contratos"
TRABALHADORES = 2

def pegar(url, tentativas=8):
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

def meses(ini, fim):
    a, m = map(int, ini.split("-")); b, n = map(int, fim.split("-"))
    while (a, m) <= (b, n):
        yield a, m
        m += 1
        if m == 13: a, m = a + 1, 1

SELECT = """select numeroControlePNCP id, numeroControlePncpCompra compra, orgaoEntidade.cnpj orgao_cnpj, orgaoEntidade.razaoSocial orgao,
  orgaoEntidade.esferaId esfera, orgaoEntidade.poderId poder, unidadeOrgao.ufSigla uf, unidadeOrgao.municipioNome municipio, unidadeOrgao.codigoIbge ibge,
  tipoPessoa tipo_pessoa, niFornecedor fornecedor_doc, nomeRazaoSocialFornecedor fornecedor, tipoContrato.nome tipo_contrato, categoriaProcesso.nome categoria,
  objetoContrato objeto, valorInicial valor_inicial, valorGlobal valor_global, valorAcumulado valor_acumulado,
  dataAssinatura data_assinatura, dataVigenciaInicio vigencia_ini, dataVigenciaFim vigencia_fim, emendaParlamentar emenda, frutoAdesao adesao, processo"""

for ano, mes in reversed(list(meses(sys.argv[1], sys.argv[2]))):
    alvo = RAIZ / f"{ano}-{mes:02d}.parquet"
    if alvo.exists():
        print("pronto:", alvo.name, flush=True); continue
    ultimo = calendar.monthrange(ano, mes)[1]
    q = f"dataInicial={ano}{mes:02d}01&dataFinal={ano}{mes:02d}{ultimo}&tamanhoPagina=500"
    p1 = pegar(f"{BASE}?{q}&pagina=1")
    if not p1: print("falhou primeira página", ano, mes, flush=True); continue
    total = p1.get("totalPaginas", 1)
    print(f"{ano}-{mes:02d}: {p1.get('totalRegistros')} contratos em {total} páginas", flush=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="pncp_")) / "m.jsonl"
    falhas = []
    with tmp.open("w", encoding="utf-8") as f, ThreadPoolExecutor(TRABALHADORES) as ex:
        for d in p1["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n")
        for pg, r in zip(range(2, total + 1), ex.map(lambda p: pegar(f"{BASE}?{q}&pagina={p}"), range(2, total + 1))):
            if r is None: falhas.append(pg); continue
            for d in r["data"]: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    duckdb.sql(f"COPY ({SELECT} from read_json_auto('{tmp.as_posix()}', union_by_name=true, sample_size=-1, maximum_object_size=33554432)) TO '{alvo.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    tmp.unlink()
    print(f"ok {alvo.name} (falhas: {falhas})", flush=True)
print("FIM", flush=True)

