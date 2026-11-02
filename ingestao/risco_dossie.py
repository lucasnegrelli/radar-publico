"""Dossiê automático dos alertas financeiros (RF01): para cada banco em observação, junta
balanço (lucro, carteira de crédito), notícias (Google Notícias) e menções em diários oficiais (Querido Diário).
Lê e reescreve web/public/data/risco.json. Rodar depois de risco_financeiro.py. Falha de rede não derruba nada."""
import json, re, time, html, pathlib, unicodedata, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent
ARQ = RAIZ / "web/public/data/risco.json"
R = json.loads(ARQ.read_text(encoding="utf-8"))
c = duckdb.connect(":memory:")
norm = lambda s: "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")
bi = lambda v: "–" if v is None else f"R$ {v/1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
UA = "radar-publico/0.1 (+github.com/lucasnegrelli/radar-publico)"

def balanco(cod, ate):
    rows = c.execute(f"""select Coluna, Saldo from read_parquet('{(RAIZ/'dados/bcb/ifdata_resumo.parquet').as_posix()}')
        where CodInst=? and AnoMes=?""", [cod, ate]).fetchall()
    d = {}
    for k, v in rows:
        k = k.lower()
        if "lucro" in k: d["lucro"] = v
        elif "carteira" in k: d["carteira"] = v
        elif "ativo total" in k: d["ativo"] = v
    return d

def noticias(nome):
    q = urllib.parse.urlencode({"q": f'"{nome}"', "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
    try:
        raiz = ET.fromstring(urllib.request.urlopen(urllib.request.Request("https://news.google.com/rss/search?" + q, headers={"User-Agent": UA}), timeout=40).read())
    except Exception:
        return []
    out, chave = [], norm(nome)[:20]
    for it in raiz.iter("item"):
        t = html.unescape(it.findtext("title", "")).strip(); f = (it.findtext("source") or "").strip()
        t = re.sub(r"\s+-\s+" + re.escape(f) + r"$", "", t) if f else t
        if chave not in norm(t): continue
        try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception: d = ""
        out.append((d, f, t, it.findtext("link", "")))
    return sorted(out, reverse=True)[:5]

def diarios(nome):
    q = urllib.parse.urlencode({"querystring": f'"{nome}"', "published_since": "2024-01-01", "size": 8, "excerpt_size": 280, "number_of_excerpts": 1, "sort_by": "descending_date"})
    for t in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://api.queridodiario.org.br/gazettes?{q}", headers={"accept": "application/json", "User-Agent": UA}), timeout=60) as r:
                g = json.loads(r.read())
            return g.get("total_gazettes", 0), [(x.get("date"), x.get("territory_name"), x.get("state_code"), " ".join((x.get("excerpts") or [""])[0].split()), x.get("url") or x.get("txt_url")) for x in g.get("gazettes", [])[:4]]
        except Exception:
            time.sleep(4 * (t + 1))
    return None, []

for a in R["alertas"]:
    nome = re.sub(r"\b(S/?A|BANCO|- PRUDENCIAL)\b", "", a["empresa"], flags=re.I).strip(" -.,")
    nome_busca = a["empresa"].replace(" - PRUDENCIAL", "")
    a["secoes"] = [s for s in a["secoes"] if not s["titulo"].startswith(("Balanço", "Na imprensa", "Diários oficiais"))]
    cod = a["id"].split("-")[1]
    b = balanco(cod, R["ultimo_trimestre"])
    kv = []
    if b.get("lucro") is not None: kv.append(["Lucro líquido (trimestre)", bi(b["lucro"])])
    if b.get("carteira") is not None and b.get("ativo"): kv.append(["Carteira de crédito", f'{bi(b["carteira"])} ({100*b["carteira"]/b["ativo"]:.0f}% do ativo)'])
    if kv: a["secoes"].insert(0, {"titulo": "Balanço (Banco Central)", "kv": kv})
    n = noticias(nome_busca)
    a["secoes"].append({"titulo": "Na imprensa", "kv": [[f"{d} · {f}", f"{t} — {u}"] for d, f, t, u in n]} if n else {"titulo": "Na imprensa", "kv": [["Resultado", "Nenhuma manchete recente citando o banco."]]})
    tot, ds = diarios(nome_busca)
    if tot:
        a["secoes"].append({"titulo": "Diários oficiais (Querido Diário)", "kv": [["Menções desde 2024", f"{tot} diário(s) municipal(is)"]] + [[f"{d} · {cid}/{uf}", f"{tr} — {u}"] for d, cid, uf, tr, u in ds]})
    print(nome_busca, "| notícias:", len(n), "| diários:", tot, flush=True)
    time.sleep(1)
ARQ.write_text(json.dumps(R, ensure_ascii=False, default=str), encoding="utf-8")
# bancos em observação entram na busca de diários oficiais que roda no GitHub Actions (diarios.py)
(RAIZ / "data-publica/empresas_rf.json").write_text(json.dumps([{"id": a["id"], "empresa": a["empresa"], "uf": None} for a in R["alertas"]], ensure_ascii=False), encoding="utf-8")
print("ok", len(R["alertas"]), "dossiês financeiros")
