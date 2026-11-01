"""Notícias brasileiras sobre gasto público/corrupção. Fonte: RSS do Google Notícias (sem chave).
Saída: web/public/data/noticias.json"""
import json, time, pathlib, urllib.parse, urllib.request, xml.etree.ElementTree as ET, html, re
SAIDA = pathlib.Path(__file__).parent.parent / "web" / "public" / "data" / "noticias.json"
TEMAS = ["fraude licitação", "corrupção prefeitura", "desvio verba pública", "tribunal de contas irregularidade",
         "empresa sancionada contrato governo", "banco liquidação Banco Central investigação"]
vistos, itens = set(), []
for q in TEMAS:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:3d", "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "radar-publico/0.1 (+github.com/lucasnegrelli/radar-publico)"})
        raiz = ET.fromstring(urllib.request.urlopen(req, timeout=40).read())
    except Exception as e:
        print("falhou:", q, e); continue
    for it in raiz.iter("item"):
        titulo = html.unescape(it.findtext("title", "")).strip()
        fonte = (it.findtext("source") or "").strip()
        titulo = re.sub(r"\s+-\s+" + re.escape(fonte) + r"$", "", titulo) if fonte else titulo
        link = it.findtext("link", "")
        if not titulo or titulo in vistos: continue
        vistos.add(titulo)
        itens.append({"titulo": titulo, "url": link, "fonte": fonte, "data": it.findtext("pubDate", "")})
    time.sleep(1)
from email.utils import parsedate_to_datetime
itens.sort(key=lambda x: parsedate_to_datetime(x["data"]) if x["data"] else 0, reverse=True)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps({"gerado": time.strftime("%Y-%m-%d %H:%M"), "itens": itens[:40]}, ensure_ascii=False), encoding="utf-8")
print(len(itens), "notícias")
