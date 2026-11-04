"""Apurações de veículos de jornalismo investigativo e de fiscalização -> web/public/data/apuracoes.json
Lê os feeds RSS públicos (título, link, autor e data) de veículos que publicam investigações, filtra por tema (corrupção, desvio, fraude, licitação, emendas, lavagem, improbidade...)
e conta quem mais assina. Não copia o texto das reportagens: mostra a manchete, o veículo, o autor e o link para a matéria original. Acumula com a rodada anterior (dados/apuracoes_acum.json)
porque o RSS só guarda as últimas matérias."""
import datetime, html, json, os, pathlib, re, time, unicodedata, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
UA = {"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
FEEDS = [("Agência Pública", "https://apublica.org/feed/"), ("The Intercept Brasil", "https://theintercept.com/brasil/feed/"), ("Repórter Brasil", "https://reporterbrasil.org.br/feed/"),
         ("Poder360", "https://www.poder360.com.br/feed/"), ("Metrópoles", "https://www.metropoles.com/feed"), ("ConJur", "https://www.conjur.com.br/rss.xml"),
         ("ICIJ", "https://www.icij.org/feed/"), ("Congresso em Foco", "https://www.congressoemfoco.com.br/feed"), ("Brasil de Fato", "https://www.brasildefato.com.br/feed")]
TEMA = re.compile(r"corrup|desvi|fraud|licita|emenda|lavagem|improbid|propina|ministério público|mpf|polícia federal|\bpf\b|operação|cpi|banco master|offshore|sonega|superfatur|orçamento secreto|tcu|cgu|investig|denúncia|denuncia|vazamento|panama|pandora|paradise|suborno|cartel|milícia|facção|inss|fundo de pensão|delação", re.I)
ns = {"dc": "http://purl.org/dc/elements/1.1/"}
acum_f = RAIZ / "dados/apuracoes_acum.json"; acum = json.loads(acum_f.read_text(encoding="utf-8")) if acum_f.exists() else {}
for veic, u in FEEDS:
    try: raiz = ET.fromstring(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read())
    except Exception as e: print("falhou:", veic, str(e)[:50]); continue
    for it in raiz.iter("item"):
        t = html.unescape(it.findtext("title", "")).strip(); link = it.findtext("link", "").strip()
        if not t or not link: continue
        resumo = re.sub(r"<[^>]+>", " ", html.unescape(it.findtext("description", "") or ""))
        if not TEMA.search(t + " " + resumo[:300]): continue
        try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception: d = datetime.date.today().isoformat()
        aut = (it.findtext("dc:creator", namespaces=ns) or it.findtext("author") or "").strip()
        acum[link] = {"t": t, "f": veic, "a": aut, "d": d, "u": link}
    time.sleep(0.5)
lim = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
acum = {k: v for k, v in acum.items() if v["d"] >= lim}
acum_f.parent.mkdir(exist_ok=True); acum_f.write_text(json.dumps(acum, ensure_ascii=False), encoding="utf-8")
itens = sorted(acum.values(), key=lambda x: x["d"], reverse=True)
aut = {}
for x in itens:
    for n in re.split(r",| e | and ", x["a"]):
        n = n.strip()
        if len(n) > 4 and " " in n: a = aut.setdefault((n, x["f"]), 0); aut[(n, x["f"])] = a + 1
rank = [{"nome": k[0], "veiculo": k[1], "n": v} for k, v in sorted(aut.items(), key=lambda kv: -kv[1])[:20]]
(RAIZ / "web/public/data/apuracoes.json").write_text(json.dumps({"gerado": datetime.date.today().isoformat(), "n": len(itens), "veiculos": [f[0] for f in FEEDS], "itens": itens[:150], "autores": rank}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(itens), "apurações |", len(rank), "autores | top:", [(r["nome"], r["n"]) for r in rank[:4]])
