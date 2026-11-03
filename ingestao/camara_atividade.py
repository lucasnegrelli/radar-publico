"""Atividade dos deputados federais (API de dados abertos da Câmara): foto, escolaridade, nascimento, projetos apresentados na legislatura
(PL, PLP e PEC), comissões atuais e frentes parlamentares. Saída: dados/camara_atividade.json (id -> dados), lido por pessoas.py.
Fonte: https://dadosabertos.camara.leg.br"""
import json, os, re, time, pathlib, urllib.request, urllib.parse, unicodedata
from concurrent.futures import ThreadPoolExecutor
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
B = "https://dadosabertos.camara.leg.br/api/v2"
UA = "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"

def get(url, tent=3):
    for t in range(tent):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"accept": "application/json", "User-Agent": UA}), timeout=40)
            return json.loads(r.read())
        except Exception:
            time.sleep(2 * (t + 1))
    return None

def total(url):
    """total de itens: pede 1 item e lê o número da última página"""
    d = get(url + ("&" if "?" in url else "?") + "itens=1")
    if not d: return None
    for l in d.get("links", []):
        if l.get("rel") == "last":
            m = re.search(r"pagina=(\d+)", l["href"])
            return int(m.group(1)) if m else len(d["dados"])
    return len(d.get("dados", []))

c = duckdb.connect("dados/radar.duckdb", read_only=True)
deps = c.execute("select id, nome, siglaPartido, siglaUf, urlFoto from camara_deputados").fetchall()
print(len(deps), "deputados", flush=True)

def um(r):
    i, nome, partido, uf, foto = r
    d = (get(f"{B}/deputados/{i}") or {}).get("dados") or {}
    pl = total(f"{B}/proposicoes?idDeputadoAutor={i}&siglaTipo=PL,PLP,PEC&dataApresentacaoInicio=2023-02-01")
    org = (get(f"{B}/deputados/{i}/orgaos?dataInicio=2023-02-01&itens=100") or {}).get("dados") or []
    fr = total(f"{B}/deputados/{i}/frentes")
    atuais = [{"sigla": o["siglaOrgao"], "nome": o["nomeOrgao"], "titulo": o.get("titulo")} for o in org if not o.get("dataFim") and o.get("siglaOrgao") not in ("PLEN",)][:6]
    return str(i), {"nome": nome, "partido": partido, "uf": uf, "foto": foto, "escolaridade": d.get("escolaridade"), "nascimento": d.get("dataNascimento"), "natural": d.get("municipioNascimento"),
                    "nome_civil": (d.get("nomeCivil") or "").title(), "projetos": pl, "frentes": fr, "comissoes": atuais}

saida = {}
with ThreadPoolExecutor(8) as ex:
    for k, v in ex.map(um, deps):
        saida[k] = v
(RAIZ / "dados" / "camara_atividade.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print(len(saida), "deputados com atividade; exemplo:", next(iter(saida.values())))
