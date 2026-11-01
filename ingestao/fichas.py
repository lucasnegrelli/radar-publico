"""Fichas de agente público -> web/public/data/fichas.json
Só dados abertos e agregados (gasto de cota, fornecedores, alertas ligados). Nunca veredito."""
import json, os, pathlib, datetime, duckdb
RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
c = duckdb.connect("dados/radar.duckdb", read_only=True)
alertas = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
ids = {a["id"]: a for a in alertas}
n = lambda s: "strip_accents(upper(trim(" + s + ")))"
fichas = []

# ---------- deputados federais ----------
ceap = c.execute(f"""select {n('txNomeParlamentar')} k, any_value(txNomeParlamentar) nome, any_value(sgPartido) p, any_value(sgUF) u,
   numAno::int ano, round(sum(try_cast(vlrLiquido as double)),2) v, count(*) n from camara_ceap group by k, ano""").fetchall()
forn = c.execute(f"""select k, nome_f, v from (select {n('txNomeParlamentar')} k, txtFornecedor nome_f, sum(try_cast(vlrLiquido as double)) v,
   row_number() over (partition by {n('txNomeParlamentar')} order by sum(try_cast(vlrLiquido as double)) desc) r from camara_ceap where numAno::int >= 2023 group by 1,2) where r <= 5""").fetchall()
por = {}
for k, nome, p, u, ano, v, nn in ceap:
    d = por.setdefault(k, {"nome": nome, "p": p, "u": u, "anos": {}})
    d["anos"][ano] = v
    if p: d["p"] = p
    if u and u != "NA": d["u"] = u
tops = {}
for k, nf, v in forn: tops.setdefault(k, []).append([nf, round(v)])
# percentil do gasto 2025
v25 = sorted(d["anos"].get(2025, 0) for d in por.values() if d["anos"].get(2025, 0) > 0)
# alertas R01 por parlamentar
a01 = c.execute(f"select {n('parlamentar')} k, cnpj from alerta01 where casa='Câmara'").fetchall()
alv = {}
for k, cn in a01: alv.setdefault(k, set()).add("R01-" + cn)
for k, d in por.items():
    tot25 = d["anos"].get(2025, 0)
    pct = round(100 * sum(1 for x in v25 if x <= tot25) / len(v25)) if tot25 > 0 and v25 else None
    f = {"t": "dep", "n": d["nome"], "p": d["p"], "u": d["u"], "anos": {str(a): round(v) for a, v in sorted(d["anos"].items())}, "pct25": pct,
         "forn": tops.get(k, []), "alertas": [i for i in sorted(alv.get(k, [])) if i in ids], "n_alertas": len(alv.get(k, []))}
    fichas.append(f)

# ---------- senadores (CEAPS) ----------
sen = c.execute(f"""select any_value(SENADOR), ANO, round(sum(try_cast(replace(VALOR_REEMBOLSADO,',','.') as double)),2) from senado_ceaps group by {n('SENADOR')}, ANO""").fetchall()
sp = {}
for nome, ano, v in sen: sp.setdefault(nome, {})[ano] = round(v or 0)
a01s = c.execute(f"select parlamentar, cnpj from alerta01 where casa='Senado'").fetchall()
als = {}
for nome, cn in a01s: als.setdefault(nome.upper(), set()).add("R01-" + cn)
for nome, anos in sp.items():
    ids_s = sorted(i for i in als.get(nome.upper(), []) if i in ids)
    fichas.append({"t": "sen", "n": nome.title(), "p": None, "u": None, "anos": {str(a): v for a, v in sorted(anos.items())}, "forn": [], "alertas": ids_s, "n_alertas": len(als.get(nome.upper(), []))})

# ---------- prefeitos eleitos 2024 ----------
pref = c.execute("""select NM_CANDIDATO, SG_PARTIDO, SG_UF, NM_UE from tse_cand where DS_CARGO='PREFEITO' and DS_SIT_TOT_TURNO like 'ELEITO%'""").fetchall()
r05 = {}
try:
    for uf, mun, doc, val in c.execute("select uf, strip_accents(upper(municipio)), doc, sum(valor) from t_R05 group by 1,2,3").fetchall():
        d = r05.setdefault((uf, mun), {"n": 0, "v": 0.0}); d["n"] += 1; d["v"] += val
except Exception: pass
for nome, part, uf, cid in pref:
    k = (uf, c.execute("select strip_accents(upper(?))", [cid]).fetchone()[0]); d = r05.get(k)
    al = [a["id"] for a in alertas if a["regra"] == "R05" and a.get("manchete", {}).get("uf") == uf and (a["manchete"].get("cidade") or "").upper() == cid.upper().replace("Á","A") ][:0]
    fichas.append({"t": "pref", "n": nome.title(), "p": part, "u": uf, "c": cid.title(), "r05": d, "alertas": [], "n_alertas": d["n"] if d else 0})
# liga alertas R05 por cidade (ids do painel)
idx = {}
for a in alertas:
    if a["regra"] == "R05": idx.setdefault(((a["manchete"].get("uf") or ""), (a["manchete"].get("cidade") or "").upper()), []).append(a["id"])
for f in fichas:
    if f["t"] == "pref": f["alertas"] = idx.get((f["u"], f["c"].upper()), [])

(RAIZ / "web/public/data/fichas.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "fichas": fichas}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(fichas), "fichas:", {t: sum(1 for f in fichas if f["t"] == t) for t in ("dep", "sen", "pref")}, "|", round((RAIZ / "web/public/data/fichas.json").stat().st_size / 1e6, 1), "MB")
