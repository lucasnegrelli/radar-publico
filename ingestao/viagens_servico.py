"""Viagens a serviço do Executivo federal -> web/public/data/viagens_exec.json
Fonte: Portal da Transparência, conjunto "Viagens" (dados abertos, sem chave). Arquivos Viagem e Trecho, um zip por ano.
Só viagens com destino fora do Brasil. Nome da pessoa só aparece para função de direção (DAS 5/6 ou equivalente, natureza especial);
as demais entram apenas como cargo + órgão. A data é a do período informado na viagem; o Portal publica com atraso de semanas,
então isto NÃO é localização em tempo real."""
import json, os, re, sys, zipfile, pathlib, datetime, unicodedata, urllib.request
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
D = RAIZ / "dados/bruto/viagens"; D.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
hoje = datetime.date.today()
ANOS = [hoje.year] + ([hoje.year - 1] if hoje.month <= 3 else [])


def baixar(ano):
    pasta = D / str(ano)
    if (pasta / f"{ano}_Viagem.csv").exists(): return pasta
    req = urllib.request.Request(f"https://portaldatransparencia.gov.br/download-de-dados/viagens/{ano}", headers=UA)
    z = D / f"{ano}.zip"
    with urllib.request.urlopen(req, timeout=300) as r, open(z, "wb") as f:
        while (b := r.read(1 << 20)): f.write(b)
    with zipfile.ZipFile(z) as zz: zz.extract(f"{ano}_Viagem.csv", pasta); zz.extract(f"{ano}_Trecho.csv", pasta)
    z.unlink(); return pasta


sem = lambda s: "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")
mundo = json.load(open("data-publica/estaticos/mundo.geojson", encoding="utf-8"))
PAIS = {}
for f in mundo["features"]:
    p = f["properties"]; xy = (p["LABEL_Y"], p["LABEL_X"])  # lat, lon
    for k in ("NAME_PT", "NAME_EN", "NAME", "ADMIN"):
        if p.get(k): PAIS[sem(p[k])] = (p.get("NAME_PT") or p["NAME"], *xy)
ALIAS = {"estados unidos da america": "estados unidos", "coreia do sul": "coreia do sul", "emirados arabes": "emirados arabes unidos", "guiana (guiana inglesa)": "guiana",
         "russia": "russia", "reino unido": "reino unido", "cingapura": "singapura", "hong kong": "hong kong", "paises baixos": "paises baixos", "republica tcheca": "tchequia",
         "antartica": "antartida", "vietna": "vietna", "congo": "republica democratica do congo", "coreia do norte": "coreia do norte", "taiwan (formosa)": "taiwan", "palestina": "palestina"}


def achar(nome):
    k = sem(nome).strip(); k = ALIAS.get(k, k)
    if k in PAIS: return PAIS[k]
    c = [v for kk, v in PAIS.items() if k and (kk.startswith(k) or k.startswith(kk))]
    return c[0] if c else None


def senior(desc, cargo):
    d, c = (desc or ""), (cargo or "")
    m = re.match(r"^(CCX|FEX|CCE|FCE)[- ]?(\d{2})(\d{2})", d)  # ex.: CCX-0117 = tipo 01, nível 17 (17 e 18 equivalem aos antigos DAS 5 e 6)
    if m and int(m.group(3)) >= 17: return True
    return bool(re.search(r"natureza especial|ministro de estado", sem(d + " " + c)))


num = lambda s: float((s or "0").replace(".", "").replace(",", ".") or 0)
data = lambda s: datetime.datetime.strptime(s, "%d/%m/%Y").date().isoformat()
viagens = []
for ano in ANOS:
    try: pasta = baixar(ano)
    except Exception as e: print("sem arquivo para", ano, e); continue
    V = f"read_csv('{pasta}/{ano}_Viagem.csv',delim=';',quote='\"',encoding='latin-1',all_varchar=True,header=False,skip=1,ignore_errors=True)"
    T = f"read_csv('{pasta}/{ano}_Trecho.csv',delim=';',quote='\"',encoding='latin-1',all_varchar=True,header=False,skip=1,ignore_errors=True)"
    ext = duckdb.sql(f"select column00 id, list(distinct column08) paises, list(distinct column10) cidades from {T} where column08 <> 'Brasil' and column08 <> '' group by 1").fetchall()
    ext = {i: (p, c) for i, p, c in ext}
    for r in duckdb.sql(f"select column00,column02,column06,column08,column10,column11,column12,column13,column14,column15,column17,column18,column19,column20,column21 from {V}").fetchall():
        i, sit, orgsup, org, nome, cargo, funcao, desc, ini, fim, motivo, vd, vp, vdev, vo = r
        if i not in ext or not sit or not sit.startswith("Realizada"): continue
        try: di, df = data(ini), data(fim)
        except Exception: continue
        paises, cidades = ext[i]; pts = [achar(p) for p in paises]; pts = [p for p in pts if p]
        if not pts: continue
        sr = senior(desc, cargo)
        viagens.append({"i": di, "f": df, "pais": pts[0][0], "lat": pts[0][1], "lon": pts[0][2], "paises": [p[0] for p in pts][:4], "cid": [c for c in cidades if c][:3],
            "orgsup": orgsup, "org": org, "cargo": (cargo or "").title() if cargo and cargo != "None" else "", "funcao": desc if desc and not desc.startswith("Sem inf") else "",
            "nome": (nome or "").title() if sr else None, "sr": sr,
            "v": round(num(vd) + num(vp) + num(vo) - num(vdev)), "motivo": re.sub(r"^Motivo da viagem \([^)]*\):\s*", "", motivo or "")[:220]})

viagens.sort(key=lambda x: x["i"], reverse=True)
H = hoje.isoformat()
agora = [v for v in viagens if v["i"] <= H <= v["f"]]
por_pais, por_org = {}, {}
for v in viagens:
    p = por_pais.setdefault(v["pais"], {"pais": v["pais"], "lat": v["lat"], "lon": v["lon"], "n": 0, "v": 0, "org": {}}); p["n"] += 1; p["v"] += v["v"]; p["org"][v["orgsup"]] = p["org"].get(v["orgsup"], 0) + 1
    o = por_org.setdefault(v["orgsup"], {"org": v["orgsup"], "n": 0, "v": 0, "paises": {}}); o["n"] += 1; o["v"] += v["v"]; o["paises"][v["pais"]] = o["paises"].get(v["pais"], 0) + 1
top = lambda d, k=3: dict(sorted(d.items(), key=lambda kv: -kv[1])[:k])
saida = {"gerado": H, "ate": viagens[0]["i"] if viagens else None,
    "nota": "Viagens a serviço do Executivo federal com destino no exterior (Portal da Transparência). Período informado pelo órgão; publicação com atraso. Nome só para funções de direção.",
    "total": len(viagens), "valor": sum(v["v"] for v in viagens), "agora": agora[:200],
    "paises": sorted(({**p, "org": top(p["org"])} for p in por_pais.values()), key=lambda p: -p["n"]),
    "orgaos": sorted(({**o, "paises": top(o["paises"])} for o in por_org.values()), key=lambda o: -o["n"])[:60],
    "viagens": [v for v in viagens if v["sr"]][:1500]}
(RAIZ / "web/public/data/viagens_exec.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(viagens), "viagens ao exterior |", sum(v["sr"] for v in viagens), "de direção |", len(agora), "em curso hoje | R$", round(sum(v["v"] for v in viagens) / 1e6), "mi | até", saida["ate"])
