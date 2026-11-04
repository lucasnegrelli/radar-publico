"""Comércio exterior do Brasil por país (Comex Stat, MDIC, API pública sem chave) -> web/public/data/comex.json
Últimos 12 meses fechados, exportação e importação em US$ FOB, mais os principais produtos de cada fluxo. Marca os países da lista de sigilo/baixa tributação
mais clássica (Panamá, Ilhas Virgens, Cayman, Bahamas...). Comercializar com esses países é legal e muitas vezes tem razão econômica: o marcador só aponta
onde olhar com mais cuidado (preço, intermediários, quem é o dono final). A API limita a 1 pedido a cada ~10 s; o script espera."""
import datetime, json, os, pathlib, time, unicodedata, urllib.error, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
URL = "https://api-comexstat.mdic.gov.br/general"
H = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
sem = lambda s: "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn").strip()


def post(flow, de, ate, det):
    corpo = {"flow": flow, "monthDetail": False, "period": {"from": de, "to": ate}, "details": det, "metrics": ["metricFOB", "metricKG"], "filters": []}
    for i in range(8):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(URL, data=json.dumps(corpo).encode(), headers=H), timeout=120).read()).get("data", {}).get("list", [])
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(12 + 4 * i); continue
            print("erro", e.code); return []
        except Exception: time.sleep(5)
    return []


def por_anos(flow, de, ate, det):
    y1, y2 = int(de[:4]), int(ate[:4]); saida = []
    for y in range(y1, y2 + 1):
        a = de if y == y1 else f"{y}-01"; b = ate if y == y2 else f"{y}-12"
        saida += post(flow, a, b, det); time.sleep(11)
    return saida
def somar(ym, n):
    y, m = map(int, ym.split("-")); t = y * 12 + (m - 1) + n; return f"{t // 12}-{t % 12 + 1:02d}"
hoje = datetime.date.today(); ate = de = None
for k in (1, 2, 3, 4):
    ate = somar(hoje.strftime("%Y-%m"), -k); de = somar(ate, -11)
    teste = post("export", ate, ate, ["country"]); time.sleep(11)
    if teste: break
print("janela:", de, "a", ate, flush=True)
dados = {}
for fluxo in ("export", "import"):
    for x in por_anos(fluxo, de, ate, ["country"]):
        c = dados.setdefault(x["country"], {"pais": x["country"], "exp": 0, "imp": 0, "kg_exp": 0, "kg_imp": 0})
        c["exp" if fluxo == "export" else "imp"] += int(x["metricFOB"]); c["kg_" + ("exp" if fluxo == "export" else "imp")] += int(x["metricKG"])
prod = {}
for fluxo in ("export", "import"):
    soma = {}
    for x in por_anos(fluxo, de, ate, ["section"]): k = x.get("section") or x.get("sh2") or x.get("coSh2"); soma[k] = soma.get(k, 0) + int(x["metricFOB"])
    prod[fluxo] = [{"produto": k, "v": v} for k, v in sorted(soma.items(), key=lambda kv: -kv[1])[:8]]

mundo = json.load(open("data-publica/estaticos/mundo.geojson", encoding="utf-8")); PAIS = {}
for f in mundo["features"]:
    p = f["properties"]
    for k in ("NAME_PT", "NAME_EN", "NAME", "ADMIN"):
        if p.get(k): PAIS[sem(p[k])] = (p["LABEL_Y"], p["LABEL_X"])
ALIAS = {"estados unidos": "estados unidos da america", "coreia, republica sul": "coreia do sul", "coreia do sul": "coreia do sul", "russia": "russia", "reino unido": "reino unido", "paises baixos (holanda)": "paises baixos",
         "emirados arabes unidos": "emirados arabes unidos", "hong kong": "hong kong", "taiwan (formosa)": "taiwan", "singapura": "singapura", "republica tcheca": "tchequia"}
def achar(n):
    k = sem(n); k = ALIAS.get(k, k)
    if k in PAIS: return PAIS[k]
    for kk, v in PAIS.items():
        if k and (kk.startswith(k) or k.startswith(kk)): return v
SIGILO = ("panama", "ilhas virgens", "ilhas cayman", "cayman", "bahamas", "bermudas", "belize", "seychelles", "samoa", "ilhas marshall", "liechtenstein", "monaco", "andorra", "barbados", "antigua", "sao cristovao", "santa lucia", "sao vicente", "granada", "dominica", "vanuatu", "nauru", "ilhas cook", "maldivas", "gibraltar", "ilha de man", "anguilla", "montserrat", "turcas")
lista = []
for c in dados.values():
    xy = achar(c["pais"]); tot = c["exp"] + c["imp"]
    if not xy or tot < 5e6: continue
    lista.append({**c, "lat": xy[0], "lon": xy[1], "total": tot, "sigilo": any(sem(c["pais"]) == s or sem(c["pais"]).startswith(s + " ") or sem(c["pais"]).startswith(s + ",") for s in SIGILO)})
lista.sort(key=lambda c: -c["total"])
tot_exp, tot_imp = sum(c["exp"] for c in dados.values()), sum(c["imp"] for c in dados.values())
sig = [c for c in lista if c["sigilo"]]
saida = {"gerado": hoje.isoformat(), "fonte": "Comex Stat (MDIC)", "de": de, "ate": ate, "exp": tot_exp, "imp": tot_imp, "saldo": tot_exp - tot_imp, "produtos": prod,
         "sigilo": {"exp": sum(c["exp"] for c in sig), "imp": sum(c["imp"] for c in sig), "n": len(sig)}, "paises": lista[:80]}
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data/comex.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(lista), "países | exp US$", round(tot_exp / 1e9, 1), "bi | imp US$", round(tot_imp / 1e9, 1), "bi | sigilo:", [c["pais"] for c in sig][:8])
