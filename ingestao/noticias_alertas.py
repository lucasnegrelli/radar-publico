"""Notícias por alerta: busca o nome da empresa (frase exata) no Google Notícias e guarda até 3 manchetes.
Saída: data-publica/noticias_alertas.json  (id do alerta -> manchetes). Só mantém manchete que cita o nome."""
import json, re, time, html, pathlib, unicodedata, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
RAIZ = pathlib.Path(__file__).parent.parent
A = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
ordem = {"alta": 0, "media": 1, "baixa": 2}
norm = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
alvo = [a for a in sorted(A, key=lambda a: (ordem[a["gravidade"]], -a["total"])) if a["regra"] != "RF01" and len(a["empresa"]) >= 12][:300]
saida = {}
for i, a in enumerate(alvo):
    nome = re.sub(r"\b(LTDA|EIRELI|S/?A|ME|EPP|SA)\b\.?", "", a["empresa"], flags=re.I).strip(" -.,")
    q = urllib.parse.urlencode({"q": f'"{nome}"', "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
    try:
        req = urllib.request.Request("https://news.google.com/rss/search?" + q, headers={"User-Agent": "radar-publico/0.1 (+github.com/lucasnegrelli/radar-publico)"})
        raiz = ET.fromstring(urllib.request.urlopen(req, timeout=40).read())
    except Exception:
        time.sleep(3); continue
    itens, chave = [], norm(nome)[:24]
    for it in raiz.iter("item"):
        t = html.unescape(it.findtext("title", "")).strip(); f = (it.findtext("source") or "").strip()
        t = re.sub(r"\s+-\s+" + re.escape(f) + r"$", "", t) if f else t
        if chave not in norm(t): continue
        try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception: d = ""
        itens.append({"t": t, "f": f, "d": d, "u": it.findtext("link", "")})
    if itens: saida[a["id"]] = sorted(itens, key=lambda x: x["d"], reverse=True)[:3]
    if i % 50 == 0: print(i, "/", len(alvo), "| com notícia:", len(saida), flush=True)
    time.sleep(0.8)
(RAIZ / "data-publica/noticias_alertas.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print("FIM", len(saida), "alertas com notícia citando a empresa")
