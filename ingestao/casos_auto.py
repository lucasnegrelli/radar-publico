"""Monta web/public/data/casos.json: o dossiê financeiro do Banco Master (data-publica/casos_master.json) + os casos de pessoas expostas
politicamente (casos/*.json: resumo, situação processual e marcos com FONTE, escritos de forma a separar decisão judicial, investigação, reportagem e defesa).
Para cada caso junta, automaticamente: manchetes recentes (Google Notícias), fichas das pessoas citadas e alertas do Radar ligados ao tema.
Regra editorial: nunca afirma culpa; só registra decisões, investigações, reportagens e versões da defesa, sempre com fonte."""
import json, re, time, html, glob, pathlib, unicodedata, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RAIZ = pathlib.Path(__file__).parent.parent
UA = "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")).strip()

base = json.loads((RAIZ / "data-publica" / "casos_master.json").read_text(encoding="utf-8"))
for c in base["casos"]:
    c.setdefault("tipo", "financeiro"); c.setdefault("ordem", 0)
idx_f = RAIZ / "web/public/data/pessoas/idx.json"
idx = json.loads(idx_f.read_text(encoding="utf-8"))["p"] if idx_f.exists() else []
por_nome = {}
for r in idx:   # r = [id, nome, urna, partido, uf, cargo, ano, rank]
    for k in {norm(r[1]), norm(r[2])}:
        if k and (k not in por_nome or r[7] > por_nome[k][7]): por_nome[k] = r
al_f = RAIZ / "web/public/data/alertas.json"
alertas = json.loads(al_f.read_text(encoding="utf-8"))["alertas"] if al_f.exists() else []

def noticias(consultas):
    vistos, out = set(), []
    for q in consultas:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:365d", "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
        try:
            raiz = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read())
        except Exception:
            continue
        for it in raiz.iter("item"):
            f = (it.findtext("source") or "").strip()
            t = html.unescape(it.findtext("title", "")).strip(); t = re.sub(r"\s+-\s+" + re.escape(f) + r"$", "", t) if f else t
            if not t or t in vistos: continue
            vistos.add(t)
            try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
            except Exception: d = ""
            out.append({"data": d, "titulo": t, "fonte": f, "url": it.findtext("link", "")})
        time.sleep(1)
    return sorted(out, key=lambda x: x["data"], reverse=True)[:14]

novos = []
for f in sorted(glob.glob(str(RAIZ / "casos" / "*.json"))):
    if f.endswith("_consultas.json"): continue
    c = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    c["pessoas"] = [{"nome": n, "id": (por_nome.get(norm(n)) or [None])[0]} for n in c.get("pessoas", [])]
    c["noticias"] = noticias(c.get("consultas", []))
    c["alertas"] = []
    for regra in c.get("alertas_regras", []):
        c["alertas"] += [{"id": a["id"], "empresa": a["empresa"], "total": a["total"], "regra": a["regra"]} for a in sorted((x for x in alertas if x["regra"] == regra), key=lambda x: -x["total"])[:6]]
    c["gerado"] = time.strftime("%Y-%m-%d")
    c["marcos"] = sorted(c.get("marcos", []), key=lambda m: m["data"])
    novos.append(c)
    print(c["id"], "| manchetes:", len(c["noticias"]), "| pessoas com ficha:", sum(1 for p in c["pessoas"] if p["id"]), "/", len(c["pessoas"]), flush=True)
casos = sorted(novos, key=lambda c: c.get("ordem", 99)) + base["casos"]
out = RAIZ / "web/public/data"; out.mkdir(parents=True, exist_ok=True)
(out / "casos.json").write_text(json.dumps({"casos": casos}, ensure_ascii=False), encoding="utf-8")
print(len(casos), "casos")
