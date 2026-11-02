"""Voos internacionais pagos com a cota parlamentar (Câmara) -> web/public/data/viagens.json
Fonte: CEAP (campo 'trecho' das passagens aéreas) + aeroportos OpenFlights. A data é a da EMISSÃO da passagem, não do voo."""
import json, os, re, pathlib, datetime, duckdb

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
c = duckdb.connect("dados/radar.duckdb", read_only=True)
ap = duckdb.sql("""select column01 nome, column02 cidade, column03 pais, column04 iata, try_cast(column06 as double) lat, try_cast(column07 as double) lon
  from read_csv('dados/ref/airports.dat', header=false, all_varchar=true, quote='"', escape='"', null_padding=true) where column04 <> '\\N' and length(column04)=3""").fetchall()
AERO = {iata: {"nome": n, "cidade": ci, "pais": p, "lat": la, "lon": lo} for n, ci, p, iata, la, lo in ap}
PARAISOS = set()  # viajar a um país não é indício de nada: a lista de jurisdições favorecidas só é usada na regra de sócios estrangeiros (R08)

rows = c.execute("""select txNomeParlamentar, sgPartido, sgUF, txtTrecho, txtPassageiro, left(datEmissao,10) d, try_cast(vlrLiquido as double) v, txtDescricao
   from camara_ceap where txtTrecho is not null and txtTrecho <> '' and txtDescricao ilike '%PASSAGEM%'""").fetchall()
norm = lambda s: re.sub(r"[^A-Z ]", "", (s or "").upper().replace("Á","A").replace("Ã","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ô","O").replace("Ú","U").replace("Ç","C")).strip()
voos = []
for nome, partido, uf, trecho, pas, d, v, desc in rows:
    toks = [t for t in re.split(r"[^A-Za-z]+", trecho.upper()) if len(t) == 3 and t in AERO]
    ext = [AERO[t] | {"iata": t} for t in toks if AERO[t]["pais"] != "Brazil"]
    if not ext or v is None or v <= 0: continue
    dest = ext[0]
    voos.append({"d": d, "p": nome, "pt": partido, "uf": uf if uf != "NA" else None, "t": trecho.strip().upper(), "pais": dest["pais"], "cidade": dest["cidade"], "lat": dest["lat"], "lon": dest["lon"],
                 "v": round(v, 2), "proprio": norm(pas) == norm(nome) or norm(nome) in norm(pas) or norm(pas) in norm(nome), "paraiso": dest["pais"] in PARAISOS})
voos.sort(key=lambda x: x["d"], reverse=True)
por = {}
for x in voos:
    k = x["p"]; s = por.setdefault(k, {"p": k, "pt": x["pt"], "uf": x["uf"], "n": 0, "v": 0.0, "paises": {}, "n_paraiso": 0})
    s["n"] += 1; s["v"] += x["v"]; s["paises"][x["pais"]] = s["paises"].get(x["pais"], 0) + 1; s["n_paraiso"] += x["paraiso"]
resumo = sorted(({**s, "v": round(s["v"]), "paises": dict(sorted(s["paises"].items(), key=lambda kv: -kv[1])[:6])} for s in por.values()), key=lambda s: -s["v"])
paises = {}
for x in voos:
    s = paises.setdefault(x["pais"], {"pais": x["pais"], "lat": x["lat"], "lon": x["lon"], "n": 0, "v": 0.0, "paraiso": x["paraiso"]}); s["n"] += 1; s["v"] += x["v"]
(RAIZ / "web/public/data/viagens.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "nota": "Data = emissão da passagem (CEAP). Destino = 1º aeroporto fora do Brasil no trecho.",
    "voos": voos[:1500], "deputados": resumo[:200], "paises": sorted(({**s, "v": round(s["v"])} for s in paises.values()), key=lambda s: -s["v"])}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(voos), "voos internacionais |", len(por), "deputados |", len(paises), "países | paraísos:", sum(1 for x in voos if x["paraiso"]), "| total R$", round(sum(x["v"] for x in voos)))
print("top países:", [(s["pais"], s["n"]) for s in sorted(paises.values(), key=lambda s: -s["n"])[:8]])
