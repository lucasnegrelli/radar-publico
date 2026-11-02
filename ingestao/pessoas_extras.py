"""Extras das pessoas mais conhecidas: resumo da Wikipédia (CC BY-SA, com link) e manchetes recentes (Google Notícias, RSS).
Entrada: web/public/data/pessoas/idx.json  Saída: web/public/data/pessoas/extras.json   Retoma de onde parou (cache em dados/pessoas_extras_cache.json).
Uso: python pessoas_extras.py [N]   (N = quantas pessoas, padrão 2500, em ordem de relevância)"""
import json, re, sys, time, html, pathlib, unicodedata, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RAIZ = pathlib.Path(__file__).parent.parent
IDX = json.loads((RAIZ / "web/public/data/pessoas/idx.json").read_text(encoding="utf-8"))["p"]
SAIDA = RAIZ / "web/public/data/pessoas/extras.json"
CACHE = RAIZ / "dados/pessoas_extras_cache.json"
UA = "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
norm = lambda s: "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")
POL = re.compile(r"pol[ií]tic|deputad|senador|president|governador|prefeit|vereador|ministr|jurista|empres[aá]ri|militar|advogad|juiz|jornalista|economista", re.I)
cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

def get(url, tent=3):
    for t in range(tent):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"}), timeout=30).read()
        except Exception:
            time.sleep(2 * (t + 1))
    return None

def wikipedia(nomes):
    for nome in nomes:
        raw = get("https://pt.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "list": "search", "srsearch": nome + " político", "srlimit": 3, "format": "json"}))
        if not raw: continue
        for r in json.loads(raw).get("query", {}).get("search", []):
            tit = r["title"]
            ts = set(norm(nome).split()) - {"da", "de", "do", "das", "dos", "e"}
            if len(ts & set(norm(tit).replace("(", " ").replace(")", " ").split())) < min(2, len(ts)): continue
            raw2 = get("https://pt.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(tit.replace(" ", "_")))
            if not raw2: continue
            s = json.loads(raw2)
            ex = (s.get("extract") or "").strip(); desc = s.get("description") or ""
            if ex and POL.search(desc + " " + ex[:300]) and s.get("type") == "standard":
                return {"t": s.get("title"), "d": desc, "x": ex[:420] + ("…" if len(ex) > 420 else ""), "u": s["content_urls"]["desktop"]["page"]}
    return None

def noticias(nome):
    raw = get("https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f'"{nome}" when:365d', "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"}))
    if not raw: return []
    try: raiz = ET.fromstring(raw)
    except Exception: return []
    chave = norm(nome).split()[0] + " " + norm(nome).split()[-1] if len(nome.split()) > 1 else norm(nome)
    out = []
    for it in raiz.iter("item"):
        t = html.unescape(it.findtext("title", "")).strip(); f = (it.findtext("source") or "").strip()
        t = re.sub(r"\s+-\s+" + re.escape(f) + r"$", "", t) if f else t
        if not all(w in norm(t) for w in chave.split()): continue
        try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception: d = ""
        out.append([d, f, t, it.findtext("link", "")])
    return sorted(out, reverse=True)[:5]

alvo = [r for r in IDX if r[7] >= 60][:N]
print(len(alvo), "pessoas alvo", flush=True)
from concurrent.futures import ThreadPoolExecutor
def um(r):
    pid, nome, urna = r[0], r[1], r[2]
    w = wikipedia([nome]) or (wikipedia([urna]) if urna and len(urna.split()) > 1 else None)
    n = noticias(urna if urna and len(urna.split()) > 1 else nome)
    time.sleep(0.3)
    return pid, {"w": w, "n": n}
def salvar():
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    SAIDA.write_text(json.dumps({k: v for k, v in cache.items() if v["w"] or v["n"]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
pend = [r for r in alvo if r[0] not in cache]
with ThreadPoolExecutor(6) as ex:
    for i, (pid, v) in enumerate(ex.map(um, pend), 1):
        cache[pid] = v
        if i % 50 == 0:
            salvar(); print(i, "/", len(pend), "| com wiki:", sum(1 for x in cache.values() if x["w"]), "| com notícia:", sum(1 for x in cache.values() if x["n"]), flush=True)
salvar(); print("FIM", len(cache))
