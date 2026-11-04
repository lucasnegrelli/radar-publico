"""Casos com valor a partir das notícias, 100% automático e sem revisão manual -> web/public/data/casos_noticias.json
Fonte: manchetes do Google Notícias (RSS, sem chave). Regras que substituem a revisão humana:
 1. só entra manchete com valor em reais explícito (R$ ... mil/mi/milhões/bi/bilhões/tri) e palavra de apuração (desvio, fraude, lavagem, propina, rombo, golpe, superfaturamento...);
 2. manchetes do mesmo fato (valor igual com 3% de folga, em até 14 dias) viram UM caso, e o caso só é publicado se vier de 2+ veículos diferentes
    ou de fonte oficial (Polícia Federal, MPF, CGU, TCU, Banco Central, Governo Federal);
 3. o texto exibido é a própria manchete, com link; nada é reescrito nem afirma culpa. O valor é "citado em notícia", nunca prejuízo confirmado.
Opcional, quando houver ANTHROPIC_API_KEY: um modelo pode dar título e envolvidos de cada caso (ver nomear()). Sem chave, vale a manchete mais citada."""
import datetime, html, json, os, pathlib, re, time, unicodedata, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
UA = {"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
CONSULTAS = ["operação Polícia Federal desvio bilhões", "operação PF fraude milhões recursos públicos", "MPF denuncia desvio milhões", "CGU operação desvio recursos federais",
             "esquema lavagem de dinheiro bilhões", "rombo bilhões banco liquidação", "fraude bilionária investigação", "superfaturamento milhões prefeitura operação",
             "TCU irregularidade milhões contrato", "propina milhões investigação", "golpe bilhões investigação Polícia Federal", "desvio fundo de previdência milhões operação",
             "fraude INSS descontos bilhões", "emendas parlamentares desvio milhões operação", "organização criminosa lavagem fintech bilhões"]
OFICIAL = ("governo federal", "polícia federal", "ministério público", "mpf", "cgu", "tcu", "banco central", "agência brasil", "senado", "câmara dos deputados", "policia federal")
CHAVES = r"desvi|fraud|lavagem|propina|rombo|golpe|superfatur|corrup|esquema|prejuízo|sonega|calote|improbidade|organização criminosa|operação|liquidação|liquidacao"
VAL = re.compile(r"R\$\s*([\d\.]+(?:,\d+)?)\s*(mil(?:hões|hão)?|mi\b|milh[õo]es|milh[ãa]o|bi\b|bilh[õo]es|bilh[ãa]o|tri\b|trilh[õo]es|trilh[ãa]o)?", re.I)
MULT = {"mil": 1e3, "mi": 1e6, "milhao": 1e6, "milhoes": 1e6, "bi": 1e9, "bilhao": 1e9, "bilhoes": 1e9, "tri": 1e12, "trilhao": 1e12, "trilhoes": 1e12}
sem = lambda s: "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")


def valor(t):
    """Maior valor em reais citado na manchete, com a unidade escrita (ou None)."""
    best = None
    for m in VAL.finditer(t):
        un = sem(m.group(2) or "")
        if not un: continue                       # "R$ 5.000" sem unidade: ignora (valor pequeno demais para o propósito)
        try: n = float(m.group(1).replace(".", "").replace(",", "."))
        except ValueError: continue
        mult = 1e12 if un.startswith("tri") else 1e9 if un.startswith("bi") else 1e6 if (un == "mi" or un.startswith("milh")) else 1e3 if un == "mil" else None
        if mult is None: continue
        v = n * mult
        if best is None or v > best: best = v
    return best


itens, vistos = [], set()
for q in CONSULTAS:
    u = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:45d", "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
    try: raiz = ET.fromstring(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read())
    except Exception as e: print("falhou:", q, str(e)[:50]); continue
    for it in raiz.iter("item"):
        fonte = (it.findtext("source") or "").strip(); t = html.unescape(it.findtext("title", "")).strip()
        t = re.sub(r"\s+[-—]\s+" + re.escape(fonte) + r"$", "", t) if fonte else t
        if not t or (t, fonte) in vistos or not re.search(CHAVES, sem(t)): continue
        vistos.add((t, fonte)); v = valor(t)
        if not v or v < 20e6 or v > 5e12: continue
        try: d = parsedate_to_datetime(it.findtext("pubDate")).date()
        except Exception: continue
        itens.append({"t": t, "f": fonte, "d": d, "v": v, "u": it.findtext("link", ""), "of": any(o in sem(fonte) or o in sem(t)[:60] for o in OFICIAL)})
    time.sleep(0.8)
print(len(itens), "manchetes com valor", flush=True)

# agrupa o mesmo fato: valor parecido (3%) e datas próximas (14 dias)
itens.sort(key=lambda x: -x["v"]); grupos = []
for x in itens:
    for g in grupos:
        if abs(x["v"] - g["v"]) / g["v"] <= 0.03 and abs((x["d"] - g["d"]).days) <= 14: g["its"].append(x); break
    else: grupos.append({"v": x["v"], "d": x["d"], "its": [x]})
casos = []
for g in grupos:
    veic = {i["f"] for i in g["its"] if i["f"]}; oficial = any(i["of"] for i in g["its"])
    if len(veic) < 2 and not oficial: continue
    its = sorted(g["its"], key=lambda i: (not i["of"], -len(i["t"])))     # oficial primeiro
    cont = {}
    for i in g["its"]: cont[i["t"]] = cont.get(i["t"], 0) + 1
    rep = its[0]["t"] if oficial else min((i["t"] for i in g["its"]), key=lambda t: abs(len(t) - 95))
    ul, vistos_f, links = max(i["d"] for i in g["its"]), set(), []
    for i in its:
        if i["f"] in vistos_f: continue
        vistos_f.add(i["f"]); links.append({"f": i["f"], "t": i["t"], "u": i["u"], "d": i["d"].isoformat()})
    ts = sem(" ".join(i["t"] for i in g["its"]))
    tipo = "evitado" if re.search(r"impede|evita|evitou|frustra|barra", sem(rep)) else "movimentado" if re.search(r"movimentou|movimentaram|movimentacao", ts) else "bloqueio" if re.search(r"bloqueio|bloqueia|apreend|sequestr", ts) else "citado"
    casos.append({"tipo": tipo, "titulo": rep, "valor": g["v"], "veiculos": len(veic), "oficial": oficial, "ultimo": ul.isoformat(), "primeiro": min(i["d"] for i in g["its"]).isoformat(), "links": links[:6]})
casos.sort(key=lambda c: (-c["valor"]))


def nomear(cs):
    """Gancho para o modelo de linguagem (opcional): só usado com ANTHROPIC_API_KEY. Pede título curto e envolvidos citados, sem acusar ninguém."""
    k = os.environ.get("ANTHROPIC_API_KEY")
    if not k: return cs
    try:
        corpo = {"model": "claude-haiku-5-5", "max_tokens": 1500, "messages": [{"role": "user", "content": "Para cada caso, devolva JSON [{\"i\":n,\"titulo\":\"até 90 caracteres, sem afirmar culpa\",\"envolvidos\":[\"nomes citados nas manchetes\"]}]. Use SÓ o que está nas manchetes.\n" + json.dumps([{"i": i, "manchetes": [l["t"] for l in c["links"][:4]]} for i, c in enumerate(cs[:40])], ensure_ascii=False)}]}
        r = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(), headers={"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"}), timeout=90).read())
        txt = r["content"][0]["text"]; arr = json.loads(txt[txt.index("["): txt.rindex("]") + 1])
        for a in arr:
            if 0 <= a.get("i", -1) < len(cs): cs[a["i"]]["titulo_ia"] = a.get("titulo"); cs[a["i"]]["envolvidos"] = a.get("envolvidos", [])[:6]
    except Exception as e: print("modelo indisponível, segue só com manchetes:", str(e)[:60])
    return cs


casos = nomear(casos)[:60]
saida = {"gerado": datetime.date.today().isoformat(), "fonte": "Google Notícias (manchetes), agrupadas automaticamente", "n": len(casos), "total": sum(c["valor"] for c in casos if c["tipo"] != "evitado"),
         "aviso": "Valores citados em notícias sobre investigações e operações. Não são prejuízo confirmado nem prova contra ninguém.", "casos": casos}
(RAIZ / "web/public/data/casos_noticias.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(casos), "casos | R$", round(saida["total"] / 1e9, 1), "bi citados |", sum(1 for c in casos if c["oficial"]), "com fonte oficial")
for c in casos[:6]: print(f"  R$ {c['valor']/1e9:.2f} bi · {c['veiculos']} veículos · {c['titulo'][:90]}")
